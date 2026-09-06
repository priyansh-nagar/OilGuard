"""
Validation-Only Threshold Analysis for Experiment 2 (Class Weight 2.5 + Robustness Augmentation)

Read-only diagnostic on the deterministic seed-42 validation split.
No test set access, no retraining, no model/dataset modification.
"""

import os
import random
import numpy as np
import torch
import torch.nn as nn
from pathlib import Path
from PIL import Image
import pandas as pd

# ============================================================================
# Configuration (identical to training scripts)
# ============================================================================

PROJECT_ROOT = Path(r"C:\Users\amit nagar\Projects\oilguard")
CSIRO_ROOT = PROJECT_ROOT / "data" / "CSIRO"
CLASS_0_DIR = CSIRO_ROOT / "S1SAR_UnBalanced_400by400_Class_0"
CLASS_1_DIR = CSIRO_ROOT / "S1SAR_UnBalanced_400by400_Class_1"

MODEL_PATH = PROJECT_ROOT / "backend" / "ml" / "outputs" / "class_weight_25" / "oil_spill_cnn_best.pt"
OUTPUT_DIR = PROJECT_ROOT / "backend" / "ml" / "outputs" / "threshold_analysis"

RANDOM_SEED = 42
TRAIN_RATIO = 0.70
VAL_RATIO = 0.15
TEST_RATIO = 0.15

DEVICE = torch.device("cpu")
THRESHOLDS = np.arange(0.10, 0.91, 0.01)  # 0.10 to 0.90 inclusive


# ============================================================================
# Model Architecture (identical to training)
# ============================================================================

class SmallCNN(nn.Module):
    def __init__(self):
        super(SmallCNN, self).__init__()
        self.conv1 = nn.Conv2d(1, 32, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm2d(32)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm2d(64)
        self.conv3 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        self.bn3 = nn.BatchNorm2d(128)
        self.pool = nn.MaxPool2d(2, 2)
        self.relu = nn.ReLU()
        self.adaptive_pool = nn.AdaptiveAvgPool2d((1, 1))
        self.fc1 = nn.Linear(128, 64)
        self.dropout = nn.Dropout(0.5)
        self.fc2 = nn.Linear(64, 1)

    def forward(self, x):
        x = self.pool(self.relu(self.bn1(self.conv1(x))))
        x = self.pool(self.relu(self.bn2(self.conv2(x))))
        x = self.pool(self.relu(self.bn3(self.conv3(x))))
        x = self.adaptive_pool(x)
        x = x.view(x.size(0), -1)
        x = self.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.fc2(x)
        return x


# ============================================================================
# Data Preparation (identical to training scripts for exact reproducibility)
# ============================================================================

def prepare_data():
    """Load and split data identically to training scripts (seed=42)."""
    class_0_images = list(CLASS_0_DIR.rglob("*.jpg"))
    class_1_images = list(CLASS_1_DIR.rglob("*.jpg"))

    class_0_labels = [0] * len(class_0_images)
    class_1_labels = [1] * len(class_1_images)

    all_images = class_0_images + class_1_images
    all_labels = class_0_labels + class_1_labels

    # Shuffle with fixed seed
    combined = list(zip(all_images, all_labels))
    random.seed(RANDOM_SEED)
    random.shuffle(combined)
    all_images, all_labels = zip(*combined)
    all_images = list(all_images)
    all_labels = list(all_labels)

    # Stratified split
    class_0_indices = [i for i, label in enumerate(all_labels) if label == 0]
    class_1_indices = [i for i, label in enumerate(all_labels) if label == 1]

    def split_indices(indices, train_ratio, val_ratio):
        n = len(indices)
        train_end = int(n * train_ratio)
        val_end = train_end + int(n * val_ratio)
        return indices[:train_end], indices[train_end:val_end], indices[val_end:]

    train_0, val_0, test_0 = split_indices(class_0_indices, TRAIN_RATIO, VAL_RATIO)
    train_1, val_1, test_1 = split_indices(class_1_indices, TRAIN_RATIO, VAL_RATIO)

    val_indices = val_0 + val_1
    random.shuffle(val_indices)

    val_images = [all_images[i] for i in val_indices]
    val_labels = [all_labels[i] for i in val_indices]

    print(f"Validation set: {len(val_labels)} images")
    print(f"  Class 0: {sum(1 for l in val_labels if l == 0)}")
    print(f"  Class 1: {sum(1 for l in val_labels if l == 1)}")

    return val_images, val_labels


# ============================================================================
# Inference
# ============================================================================

def predict_prob(model, image_path):
    """Baseline preprocessing: JPG -> grayscale -> float32 -> /255.0"""
    img = Image.open(image_path).convert("L")
    arr = np.array(img, dtype=np.float32) / 255.0
    t = torch.from_numpy(arr).unsqueeze(0).unsqueeze(0)  # (1, 1, H, W)
    with torch.no_grad():
        logit = model(t)
        return torch.sigmoid(logit).item()


def main():
    print("=" * 80)
    print("VALIDATION THRESHOLD ANALYSIS - Experiment 2 (Class Weight 2.5)")
    print("=" * 80)
    print()

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Load model
    print(f"Loading model from: {MODEL_PATH}")
    ckpt = torch.load(MODEL_PATH, map_location=DEVICE, weights_only=False)
    model = SmallCNN().to(DEVICE)
    model.load_state_dict(ckpt["model_state_dict"])
    model.eval()
    print(f"Model loaded. Validation loss from training: {ckpt.get('val_loss', 'N/A')}")
    print()

    # Get validation data (exact seed-42 split)
    val_images, val_labels = prepare_data()
    print()

    # Generate probabilities
    print("Generating validation probabilities...")
    probs = []
    for i, path in enumerate(val_images):
        if (i + 1) % 100 == 0:
            print(f"  {i+1}/{len(val_images)}")
        probs.append(predict_prob(model, path))
    probs = np.array(probs)
    labels = np.array(val_labels)

    print(f"Probability range: {probs.min():.4f} - {probs.max():.4f}")
    print(f"Mean prob (class 0): {probs[labels==0].mean():.4f}")
    print(f"Mean prob (class 1): {probs[labels==1].mean():.4f}")
    print()

    # Evaluate thresholds
    print("Evaluating thresholds 0.10 - 0.90...")
    results = []

    for thresh in THRESHOLDS:
        preds = (probs >= thresh).astype(int)

        tp = ((preds == 1) & (labels == 1)).sum()
        tn = ((preds == 0) & (labels == 0)).sum()
        fp = ((preds == 1) & (labels == 0)).sum()
        fn = ((preds == 0) & (labels == 1)).sum()

        accuracy = (tp + tn) / len(labels)
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

        results.append({
            "threshold": round(thresh, 2),
            "accuracy": round(accuracy, 4),
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "oil_f1": round(f1, 4),
            "tp": int(tp),
            "tn": int(tn),
            "fp": int(fp),
            "fn": int(fn),
        })

    df = pd.DataFrame(results)

    # Save CSV
    csv_path = OUTPUT_DIR / "validation_threshold_analysis.csv"
    df.to_csv(csv_path, index=False)
    print(f"CSV saved: {csv_path}")
    print()

    # Find optimal thresholds
    max_f1_idx = df["oil_f1"].idxmax()
    max_acc_idx = df["accuracy"].idxmax()

    # Best precision with recall >= 0.70
    recall_ge_70 = df[df["recall"] >= 0.70]
    if len(recall_ge_70) > 0:
        best_prec_70_idx = recall_ge_70["precision"].idxmax()
    else:
        best_prec_70_idx = None

    # Best precision with recall >= 0.80
    recall_ge_80 = df[df["recall"] >= 0.80]
    if len(recall_ge_80) > 0:
        best_prec_80_idx = recall_ge_80["precision"].idxmax()
    else:
        best_prec_80_idx = None

    # Best F1 with recall >= 0.80
    if len(recall_ge_80) > 0:
        best_f1_80_idx = recall_ge_80["oil_f1"].idxmax()
    else:
        best_f1_80_idx = None

    # Metrics at 0.50
    row_50 = df[df["threshold"] == 0.50].iloc[0]

    # Build Markdown report
    lines = []
    lines.append("# Validation Threshold Analysis: Experiment 2 (Class Weight 2.5 + Robustness Augmentation)")
    lines.append("")
    lines.append("## Scope and Safeguards")
    lines.append("")
    lines.append("Read-only diagnostic on the deterministic seed-42 validation split (843 images).")
    lines.append("No test set access, no retraining, no model/dataset modification.")
    lines.append("")
    lines.append(f"- Model: `outputs/class_weight_25/oil_spill_cnn_best.pt` (val_loss={ckpt.get('val_loss', 'N/A'):.4f})")
    lines.append(f"- Validation images: {len(val_labels)}")
    lines.append(f"- Preprocessing: JPG -> grayscale -> float32 -> /255.0 (baseline only)")
    lines.append(f"- Thresholds evaluated: {THRESHOLDS[0]:.2f} to {THRESHOLDS[-1]:.2f} step 0.01")
    lines.append("")

    # Full table
    lines.append("## Full Threshold Sweep")
    lines.append("")
    lines.append("| Threshold | Accuracy | Precision | Recall | Oil F1 | TP | TN | FP | FN |")
    lines.append("|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for _, r in df.iterrows():
        lines.append(f"| {r['threshold']:.2f} | {r['accuracy']:.4f} | {r['precision']:.4f} | {r['recall']:.4f} | {r['oil_f1']:.4f} | {r['tp']} | {r['tn']} | {r['fp']} | {r['fn']} |")
    lines.append("")

    # Optimal thresholds
    lines.append("## Optimal Thresholds (Validation Set)")
    lines.append("")

    r = df.iloc[max_f1_idx]
    lines.append(f"### 1. Maximum Oil F1")
    lines.append(f"- Threshold: **{r['threshold']:.2f}**")
    lines.append(f"- F1: {r['oil_f1']:.4f}, Precision: {r['precision']:.4f}, Recall: {r['recall']:.4f}, Accuracy: {r['accuracy']:.4f}")
    lines.append(f"- Confusion Matrix: TP={r['tp']}, TN={r['tn']}, FP={r['fp']}, FN={r['fn']}")
    lines.append("")

    r = df.iloc[max_acc_idx]
    lines.append(f"### 2. Maximum Accuracy")
    lines.append(f"- Threshold: **{r['threshold']:.2f}**")
    lines.append(f"- Accuracy: {r['accuracy']:.4f}, F1: {r['oil_f1']:.4f}, Precision: {r['precision']:.4f}, Recall: {r['recall']:.4f}")
    lines.append(f"- Confusion Matrix: TP={r['tp']}, TN={r['tn']}, FP={r['fp']}, FN={r['fn']}")
    lines.append("")

    if best_prec_70_idx is not None:
        r = df.loc[best_prec_70_idx]
        lines.append(f"### 3. Best Precision with Recall >= 0.70")
        lines.append(f"- Threshold: **{r['threshold']:.2f}**")
        lines.append(f"- Precision: {r['precision']:.4f}, Recall: {r['recall']:.4f}, F1: {r['oil_f1']:.4f}, Accuracy: {r['accuracy']:.4f}")
        lines.append(f"- Confusion Matrix: TP={r['tp']}, TN={r['tn']}, FP={r['fp']}, FN={r['fn']}")
        lines.append("")
    else:
        lines.append("### 3. Best Precision with Recall >= 0.70")
        lines.append("- No threshold achieves recall >= 0.70")
        lines.append("")

    if best_prec_80_idx is not None:
        r = df.loc[best_prec_80_idx]
        lines.append(f"### 4. Best Precision with Recall >= 0.80")
        lines.append(f"- Threshold: **{r['threshold']:.2f}**")
        lines.append(f"- Precision: {r['precision']:.4f}, Recall: {r['recall']:.4f}, F1: {r['oil_f1']:.4f}, Accuracy: {r['accuracy']:.4f}")
        lines.append(f"- Confusion Matrix: TP={r['tp']}, TN={r['tn']}, FP={r['fp']}, FN={r['fn']}")
        lines.append("")
    else:
        lines.append("### 4. Best Precision with Recall >= 0.80")
        lines.append("- No threshold achieves recall >= 0.80")
        lines.append("")

    if best_f1_80_idx is not None:
        r = df.loc[best_f1_80_idx]
        lines.append(f"### 5. Best F1 with Recall >= 0.80")
        lines.append(f"- Threshold: **{r['threshold']:.2f}**")
        lines.append(f"- F1: {r['oil_f1']:.4f}, Precision: {r['precision']:.4f}, Recall: {r['recall']:.4f}, Accuracy: {r['accuracy']:.4f}")
        lines.append(f"- Confusion Matrix: TP={r['tp']}, TN={r['tn']}, FP={r['fp']}, FN={r['fn']}")
        lines.append("")
    else:
        lines.append("### 5. Best F1 with Recall >= 0.80")
        lines.append("- No threshold achieves recall >= 0.80")
        lines.append("")

    lines.append(f"### 6. Metrics at Fixed Threshold 0.50")
    lines.append(f"- Threshold: **0.50**")
    lines.append(f"- Accuracy: {row_50['accuracy']:.4f}, Precision: {row_50['precision']:.4f}, Recall: {row_50['recall']:.4f}, F1: {row_50['oil_f1']:.4f}")
    lines.append(f"- Confusion Matrix: TP={row_50['tp']}, TN={row_50['tn']}, FP={row_50['fp']}, FN={row_50['fn']}")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("*This analysis uses only the validation split. The held-out test set remains completely untouched.*")

    report = "\n".join(lines)
    md_path = OUTPUT_DIR / "VALIDATION_THRESHOLD_ANALYSIS.md"
    md_path.write_text(report, encoding="utf-8")
    print(f"Report saved: {md_path}")
    print()

    # Console summary
    print("=== SUMMARY ===")
    print(f"Max F1:      thresh={df.iloc[max_f1_idx]['threshold']:.2f}, F1={df.iloc[max_f1_idx]['oil_f1']:.4f}")
    print(f"Max Accuracy: thresh={df.iloc[max_acc_idx]['threshold']:.2f}, Acc={df.iloc[max_acc_idx]['accuracy']:.4f}")
    if best_prec_70_idx is not None:
        r = df.loc[best_prec_70_idx]
        print(f"Best Prec@Rec>=0.70: thresh={r['threshold']:.2f}, Prec={r['precision']:.4f}, Rec={r['recall']:.4f}")
    if best_prec_80_idx is not None:
        r = df.loc[best_prec_80_idx]
        print(f"Best Prec@Rec>=0.80: thresh={r['threshold']:.2f}, Prec={r['precision']:.4f}, Rec={r['recall']:.4f}")
    if best_f1_80_idx is not None:
        r = df.loc[best_f1_80_idx]
        print(f"Best F1@Rec>=0.80: thresh={r['threshold']:.2f}, F1={r['oil_f1']:.4f}, Rec={r['recall']:.4f}")
    print(f"At 0.50: Acc={row_50['accuracy']:.4f}, Prec={row_50['precision']:.4f}, Rec={row_50['recall']:.4f}, F1={row_50['oil_f1']:.4f}")


if __name__ == "__main__":
    main()