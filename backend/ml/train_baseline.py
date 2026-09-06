"""
Stage 2B: Small CNN Baseline for Oil Spill Detection

Binary classification of 400x400 SAR patches:
    Class 0 = Non-Oil
    Class 1 = Oil

This model classifies pre-cropped patches, NOT full satellite scenes.
"""

import os
import random
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from PIL import Image
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    roc_auc_score,
    classification_report,
)

# ============================================================================
# Configuration
# ============================================================================

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
CSIRO_ROOT = PROJECT_ROOT / "data" / "CSIRO"
CLASS_0_DIR = CSIRO_ROOT / "S1SAR_UnBalanced_400by400_Class_0"
CLASS_1_DIR = CSIRO_ROOT / "S1SAR_UnBalanced_400by400_Class_1"
OUTPUT_DIR = PROJECT_ROOT / "backend" / "ml" / "outputs"

# Reproducibility
RANDOM_SEED = 42
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)
torch.manual_seed(RANDOM_SEED)

# Data split
TRAIN_RATIO = 0.70
VAL_RATIO = 0.15
TEST_RATIO = 0.15

# Training hyperparameters
BATCH_SIZE = 32
LEARNING_RATE = 0.001
NUM_EPOCHS = 15
EARLY_STOP_PATIENCE = 3

# Device
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Class imbalance (from inspection: 1.96:1 ratio)
# Weight for Class 1 (oil) to handle imbalance
CLASS_WEIGHTS = torch.tensor([1.0, 1.96], dtype=torch.float32)

# Checkpoint paths
CHECKPOINT_PATH = OUTPUT_DIR / "checkpoint_latest.pt"
BEST_MODEL_PATH = OUTPUT_DIR / "oil_spill_cnn_best.pt"
FINAL_MODEL_PATH = OUTPUT_DIR / "oil_spill_cnn_baseline.pt"


# ============================================================================
# Dataset Class
# ============================================================================


class OilSpillDataset(Dataset):
    """
    Dataset for CSIRO oil spill SAR patches.

    Since R=G=B (verified), we convert to grayscale (single channel).
    """

    def __init__(self, image_paths, labels, transform=None):
        self.image_paths = image_paths
        self.labels = labels
        self.transform = transform

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        # Load image
        img_path = self.image_paths[idx]
        img = Image.open(img_path)

        # Convert to grayscale (since R=G=B)
        img = img.convert("L")

        # Convert to numpy array and normalize to [0, 1]
        img_array = np.array(img, dtype=np.float32) / 255.0

        # Add channel dimension: (H, W) -> (1, H, W)
        img_tensor = torch.from_numpy(img_array).unsqueeze(0)

        label = self.labels[idx]

        return img_tensor, label


# ============================================================================
# CNN Model
# ============================================================================


class SmallCNN(nn.Module):
    """
    Lightweight CNN for binary oil/non-oil classification.

    Input: (batch, 1, 400, 400) - single-channel grayscale SAR
    Output: (batch, 1) - binary logit (oil probability after sigmoid)

    Architecture:
        - 3 convolutional blocks with pooling
        - Adaptive Average Pooling to reduce spatial dimensions
        - Small fully connected layer
        - Binary classification head

    This design avoids the huge FC layer by using global pooling.
    Total parameters: ~300K (compared to 82M in the original design)
    """

    def __init__(self):
        super(SmallCNN, self).__init__()

        # Convolutional layers (progressively increasing channels)
        self.conv1 = nn.Conv2d(1, 32, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm2d(32)

        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm2d(64)

        self.conv3 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        self.bn3 = nn.BatchNorm2d(128)

        self.pool = nn.MaxPool2d(2, 2)
        self.relu = nn.ReLU()

        # Adaptive average pooling reduces spatial dimensions to 1x1
        # Output: (batch, 128, 1, 1) regardless of input size
        self.adaptive_pool = nn.AdaptiveAvgPool2d((1, 1))

        # Small fully connected layers
        self.fc1 = nn.Linear(128, 64)
        self.dropout = nn.Dropout(0.5)
        self.fc2 = nn.Linear(64, 1)

    def forward(self, x):
        # Conv block 1: 400x400x1 -> 200x200x32
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)
        x = self.pool(x)

        # Conv block 2: 200x200x32 -> 100x100x64
        x = self.conv2(x)
        x = self.bn2(x)
        x = self.relu(x)
        x = self.pool(x)

        # Conv block 3: 100x100x64 -> 50x50x128
        x = self.conv3(x)
        x = self.bn3(x)
        x = self.relu(x)
        x = self.pool(x)

        # Adaptive pooling: 50x50x128 -> 1x1x128
        x = self.adaptive_pool(x)

        # Flatten: 1x1x128 -> 128
        x = x.view(x.size(0), -1)

        # Fully connected layers
        x = self.fc1(x)
        x = self.relu(x)
        x = self.dropout(x)
        x = self.fc2(x)

        return x


# ============================================================================
# Data Preparation
# ============================================================================


def prepare_data():
    """
    Load and split data into train/val/test with stratification.
    """
    print("=" * 80)
    print("PREPARING DATA")
    print("=" * 80)
    print()

    # Collect all image paths
    class_0_images = list(CLASS_0_DIR.rglob("*.jpg"))
    class_1_images = list(CLASS_1_DIR.rglob("*.jpg"))

    print(f"Class 0 (Non-Oil): {len(class_0_images)} images")
    print(f"Class 1 (Oil):     {len(class_1_images)} images")
    print()

    # Create labels
    class_0_labels = [0] * len(class_0_images)
    class_1_labels = [1] * len(class_1_images)

    all_images = class_0_images + class_1_images
    all_labels = class_0_labels + class_1_labels

    # Shuffle with fixed seed
    combined = list(zip(all_images, all_labels))
    random.shuffle(combined)
    all_images, all_labels = zip(*combined)
    all_images = list(all_images)
    all_labels = list(all_labels)

    # Stratified split
    # Separate by class
    class_0_indices = [i for i, label in enumerate(all_labels) if label == 0]
    class_1_indices = [i for i, label in enumerate(all_labels) if label == 1]

    # Split each class
    def split_indices(indices, train_ratio, val_ratio):
        n = len(indices)
        train_end = int(n * train_ratio)
        val_end = train_end + int(n * val_ratio)
        return indices[:train_end], indices[train_end:val_end], indices[val_end:]

    train_0, val_0, test_0 = split_indices(class_0_indices, TRAIN_RATIO, VAL_RATIO)
    train_1, val_1, test_1 = split_indices(class_1_indices, TRAIN_RATIO, VAL_RATIO)

    # Combine
    train_indices = train_0 + train_1
    val_indices = val_0 + val_1
    test_indices = test_0 + test_1

    # Shuffle each split
    random.shuffle(train_indices)
    random.shuffle(val_indices)
    random.shuffle(test_indices)

    # Extract data
    def get_split(indices):
        return [all_images[i] for i in indices], [all_labels[i] for i in indices]

    train_images, train_labels = get_split(train_indices)
    val_images, val_labels = get_split(val_indices)
    test_images, test_labels = get_split(test_indices)

    print(f"Split sizes:")
    print(f"  Train: {len(train_labels)} images")
    print(f"    - Class 0: {sum(1 for l in train_labels if l == 0)}")
    print(f"    - Class 1: {sum(1 for l in train_labels if l == 1)}")
    print(f"  Val:   {len(val_labels)} images")
    print(f"    - Class 0: {sum(1 for l in val_labels if l == 0)}")
    print(f"    - Class 1: {sum(1 for l in val_labels if l == 1)}")
    print(f"  Test:  {len(test_labels)} images")
    print(f"    - Class 0: {sum(1 for l in test_labels if l == 0)}")
    print(f"    - Class 1: {sum(1 for l in test_labels if l == 1)}")
    print()

    return (train_images, train_labels), (val_images, val_labels), (test_images, test_labels)


# ============================================================================
# Checkpoint Functions
# ============================================================================


def save_checkpoint(epoch, model, optimizer, best_val_loss, history):
    """
    Save training checkpoint after each epoch.

    Allows resuming training if interrupted.
    """
    checkpoint = {
        'epoch': epoch,
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
        'best_val_loss': best_val_loss,
        'history': history,
        'random_seed': RANDOM_SEED,
        'config': {
            'batch_size': BATCH_SIZE,
            'learning_rate': LEARNING_RATE,
            'num_epochs': NUM_EPOCHS,
            'early_stop_patience': EARLY_STOP_PATIENCE,
        }
    }
    torch.save(checkpoint, CHECKPOINT_PATH)
    print(f"  → Checkpoint saved (epoch {epoch + 1})", flush=True)


def load_checkpoint():
    """
    Load training checkpoint if it exists.

    Returns checkpoint dict or None if no checkpoint exists.
    """
    if CHECKPOINT_PATH.exists():
        checkpoint = torch.load(CHECKPOINT_PATH)
        print(f"✓ Found checkpoint at epoch {checkpoint['epoch'] + 1}")
        print(f"  Previous best val loss: {checkpoint['best_val_loss']:.4f}")
        return checkpoint
    return None


def save_best_model(model, val_loss, val_acc):
    """
    Save the best model (lighter than full checkpoint).

    Only saves model weights, not optimizer state.
    """
    torch.save({
        'model_state_dict': model.state_dict(),
        'val_loss': val_loss,
        'val_acc': val_acc,
    }, BEST_MODEL_PATH)
    print(f"  → Best model saved (val_loss: {val_loss:.4f})", flush=True)


# ============================================================================
# Training
# ============================================================================


def train_model(model, train_loader, val_loader, criterion, optimizer, num_epochs, start_epoch=0, loaded_best_val_loss=None, loaded_history=None):
    """
    Train the model with early stopping and checkpointing.

    Args:
        start_epoch: Epoch to start from (for resume)
        loaded_best_val_loss: Previous best val loss (for resume)
        loaded_history: Previous training history (for resume)
    """
    print("=" * 80)
    print("TRAINING")
    print("=" * 80)
    print()

    if start_epoch > 0:
        print(f"Resuming training from epoch {start_epoch + 1}...")
        print()

    print(f"Starting training loop with {len(train_loader)} batches per epoch...", flush=True)
    print()

    best_val_loss = loaded_best_val_loss if loaded_best_val_loss is not None else float("inf")
    patience_counter = 0

    # Initialize or load history
    if loaded_history is not None:
        history = loaded_history
    else:
        history = {
            'train_loss': [],
            'train_acc': [],
            'val_loss': [],
            'val_acc': [],
        }

    train_start = time.time()

    for epoch in range(start_epoch, num_epochs):
        epoch_start = time.time()

        # Training phase
        model.train()
        train_loss = 0.0
        train_correct = 0
        train_total = 0

        for batch_idx, (images, labels) in enumerate(train_loader):
            images = images.to(DEVICE)
            labels = labels.to(DEVICE).float().unsqueeze(1)

            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            train_loss += loss.item()
            predictions = (torch.sigmoid(outputs) > 0.5).float()
            train_correct += (predictions == labels).sum().item()
            train_total += labels.size(0)

            # Print progress every 20 batches
            if (batch_idx + 1) % 20 == 0:
                print(f"  Epoch {epoch+1} - Batch {batch_idx+1}/{len(train_loader)} - Loss: {loss.item():.4f}", flush=True)

        train_loss /= len(train_loader)
        train_acc = train_correct / train_total

        # Validation phase
        model.eval()
        val_loss = 0.0
        val_correct = 0
        val_total = 0

        with torch.no_grad():
            for images, labels in val_loader:
                images = images.to(DEVICE)
                labels = labels.to(DEVICE).float().unsqueeze(1)

                outputs = model(images)
                loss = criterion(outputs, labels)

                val_loss += loss.item()
                predictions = (torch.sigmoid(outputs) > 0.5).float()
                val_correct += (predictions == labels).sum().item()
                val_total += labels.size(0)

        val_loss /= len(val_loader)
        val_acc = val_correct / val_total

        epoch_time = time.time() - epoch_start

        # Save to history
        history['train_loss'].append(train_loss)
        history['train_acc'].append(train_acc)
        history['val_loss'].append(val_loss)
        history['val_acc'].append(val_acc)

        print(
            f"Epoch [{epoch+1}/{num_epochs}] ({epoch_time:.1f}s) - "
            f"Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.4f} | "
            f"Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.4f}"
        )

        # Early stopping check and best model saving
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            patience_counter = 0
            save_best_model(model, val_loss, val_acc)
            print(f"  → New best validation loss: {best_val_loss:.4f}")
        else:
            patience_counter += 1
            print(f"  → No improvement ({patience_counter}/{EARLY_STOP_PATIENCE})")

        # Save checkpoint after every epoch
        save_checkpoint(epoch, model, optimizer, best_val_loss, history)

        if patience_counter >= EARLY_STOP_PATIENCE:
            print()
            print(f"Early stopping triggered after {epoch+1} epochs")
            break

    train_time = time.time() - train_start
    print()
    print(f"Training completed in {train_time:.1f} seconds ({train_time/60:.1f} minutes)")
    print()

    # Load best model weights for final evaluation
    if BEST_MODEL_PATH.exists():
        best_checkpoint = torch.load(BEST_MODEL_PATH)
        model.load_state_dict(best_checkpoint['model_state_dict'])
        print("✓ Loaded best model weights for evaluation", flush=True)

    return model, train_time, history


# ============================================================================
# Evaluation
# ============================================================================


def evaluate_model(model, test_loader):
    """
    Evaluate the model on test set and compute metrics.
    """
    print("=" * 80)
    print("EVALUATION ON TEST SET")
    print("=" * 80)
    print()

    model.eval()

    all_labels = []
    all_predictions = []
    all_probabilities = []

    with torch.no_grad():
        for images, labels in test_loader:
            images = images.to(DEVICE)

            outputs = model(images)
            probabilities = torch.sigmoid(outputs).cpu().numpy()
            predictions = (probabilities > 0.5).astype(int).flatten()

            all_labels.extend(labels.numpy())
            all_predictions.extend(predictions)
            all_probabilities.extend(probabilities.flatten())

    all_labels = np.array(all_labels)
    all_predictions = np.array(all_predictions)
    all_probabilities = np.array(all_probabilities)

    # Metrics
    accuracy = accuracy_score(all_labels, all_predictions)
    precision = precision_score(all_labels, all_predictions, zero_division=0)
    recall = recall_score(all_labels, all_predictions, zero_division=0)
    f1 = f1_score(all_labels, all_predictions, zero_division=0)
    roc_auc = roc_auc_score(all_labels, all_probabilities)
    cm = confusion_matrix(all_labels, all_predictions)

    print(f"Accuracy:  {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall:    {recall:.4f}")
    print(f"F1 Score:  {f1:.4f}")
    print(f"ROC-AUC:   {roc_auc:.4f}")
    print()

    print("Confusion Matrix:")
    print("                 Predicted")
    print("               Non-Oil  Oil")
    print(f"Actual Non-Oil   {cm[0, 0]:5d}  {cm[0, 1]:5d}")
    print(f"       Oil       {cm[1, 0]:5d}  {cm[1, 1]:5d}")
    print()

    print("Classification Report:")
    print(classification_report(all_labels, all_predictions, target_names=["Non-Oil", "Oil"]))

    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "roc_auc": roc_auc,
        "confusion_matrix": cm,
    }


# ============================================================================
# Main
# ============================================================================


def main():
    print()
    print("=" * 80)
    print("STAGE 2B: SMALL CNN BASELINE FOR OIL SPILL DETECTION")
    print("=" * 80)
    print()
    print(f"Device: {DEVICE}")
    print(f"Random seed: {RANDOM_SEED}")
    print(f"Batch size: {BATCH_SIZE}")
    print(f"Learning rate: {LEARNING_RATE}")
    print(f"Max epochs: {NUM_EPOCHS}")
    print(f"Early stop patience: {EARLY_STOP_PATIENCE}")
    print(f"Class weights: {CLASS_WEIGHTS.tolist()}")
    print()

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Prepare data
    (train_images, train_labels), (val_images, val_labels), (test_images, test_labels) = prepare_data()

    # Create datasets
    train_dataset = OilSpillDataset(train_images, train_labels)
    val_dataset = OilSpillDataset(val_images, val_labels)
    test_dataset = OilSpillDataset(test_images, test_labels)

    # Create data loaders
    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False)
    test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False)

    # Initialize model
    model = SmallCNN().to(DEVICE)

    # Count parameters
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"Model parameters: {total_params:,} (trainable: {trainable_params:,})")
    print()

    # Loss and optimizer
    criterion = nn.BCEWithLogitsLoss(pos_weight=CLASS_WEIGHTS[1].to(DEVICE))
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)

    # Check for existing checkpoint and resume if found
    checkpoint = load_checkpoint()
    start_epoch = 0
    loaded_history = None
    loaded_best_val_loss = None

    if checkpoint is not None:
        print(f"Resuming training from epoch {checkpoint['epoch'] + 1}")
        print()
        model.load_state_dict(checkpoint['model_state_dict'])
        optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        start_epoch = checkpoint['epoch'] + 1
        loaded_best_val_loss = checkpoint['best_val_loss']
        loaded_history = checkpoint['history']

    # Train
    model, train_time, history = train_model(
        model, train_loader, val_loader, criterion, optimizer, NUM_EPOCHS,
        start_epoch=start_epoch,
        loaded_best_val_loss=loaded_best_val_loss,
        loaded_history=loaded_history
    )

    # Evaluate
    metrics = evaluate_model(model, test_loader)

    # Save final model with test metrics
    torch.save(
        {
            "model_state_dict": model.state_dict(),
            "metrics": metrics,
            "history": history,
            "config": {
                "random_seed": RANDOM_SEED,
                "batch_size": BATCH_SIZE,
                "learning_rate": LEARNING_RATE,
                "num_epochs": NUM_EPOCHS,
                "train_time_seconds": train_time,
            },
        },
        FINAL_MODEL_PATH,
    )
    print(f"Final model saved to: {FINAL_MODEL_PATH}")
    print()

    # Final summary
    print("=" * 80)
    print("TRAINING SUMMARY")
    print("=" * 80)
    print()
    print(f"Training time: {train_time:.1f}s ({train_time/60:.1f} minutes)")
    print(f"Test accuracy: {metrics['accuracy']:.4f}")
    print(f"Test precision: {metrics['precision']:.4f}")
    print(f"Test recall: {metrics['recall']:.4f}")
    print(f"Test F1 score: {metrics['f1']:.4f}")
    print(f"Test ROC-AUC: {metrics['roc_auc']:.4f}")
    print()
    print("=" * 80)
    print()


if __name__ == "__main__":
    main()
