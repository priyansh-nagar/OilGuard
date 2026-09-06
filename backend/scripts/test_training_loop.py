"""
Test script to find where training crashes.
Tests backward pass, optimizer step, and loss computation.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

print("=" * 80)
print("TRAINING LOOP DIAGNOSTIC TEST")
print("=" * 80)
print()

try:
    print("[1/7] Importing modules...")
    from backend.ml.train_baseline import (
        SmallCNN,
        OilSpillDataset,
        CLASS_0_DIR,
        CLASS_1_DIR,
        DEVICE,
        CLASS_WEIGHTS,
    )
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import DataLoader
    print("✓ Imports successful")
    print()

    print("[2/7] Creating small dataset...")
    class_0_images = list(CLASS_0_DIR.rglob("*.jpg"))[:8]
    class_1_images = list(CLASS_1_DIR.rglob("*.jpg"))[:8]
    dataset = OilSpillDataset(class_0_images + class_1_images, [0]*8 + [1]*8)
    loader = DataLoader(dataset, batch_size=4, shuffle=True)
    print(f"✓ Dataset: {len(dataset)} samples, {len(loader)} batches")
    print()

    print("[3/7] Creating model and optimizer...")
    model = SmallCNN().to(DEVICE)
    criterion = nn.BCEWithLogitsLoss(pos_weight=CLASS_WEIGHTS[1].to(DEVICE))
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    print(f"✓ Model, loss, and optimizer created")
    print()

    print("[4/7] Testing single forward pass...")
    model.train()
    images, labels = next(iter(loader))
    images = images.to(DEVICE)
    labels = labels.to(DEVICE).float().unsqueeze(1)
    print(f"  Input shape: {images.shape}")
    print(f"  Labels shape: {labels.shape}")
    outputs = model(images)
    print(f"  Output shape: {outputs.shape}")
    print("✓ Forward pass successful")
    print()

    print("[5/7] Testing loss computation...")
    loss = criterion(outputs, labels)
    print(f"  Loss value: {loss.item():.4f}")
    print("✓ Loss computation successful")
    print()

    print("[6/7] Testing backward pass...")
    optimizer.zero_grad()
    loss.backward()
    print("✓ Backward pass successful")
    print()

    print("[7/7] Testing optimizer step...")
    optimizer.step()
    print("✓ Optimizer step successful")
    print()

    print("=" * 80)
    print("SIMULATING ONE FULL EPOCH")
    print("=" * 80)
    print()

    model.train()
    total_loss = 0.0
    for batch_idx, (images, labels) in enumerate(loader):
        images = images.to(DEVICE)
        labels = labels.to(DEVICE).float().unsqueeze(1)

        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        total_loss += loss.item()
        print(f"  Batch {batch_idx + 1}/{len(loader)}: loss = {loss.item():.4f}")

    avg_loss = total_loss / len(loader)
    print()
    print(f"✓ Epoch completed successfully!")
    print(f"  Average loss: {avg_loss:.4f}")
    print()

    print("=" * 80)
    print("✓ ALL TRAINING COMPONENTS WORK CORRECTLY")
    print("=" * 80)
    print()
    print("The issue must be:")
    print("  - Memory exhaustion with full dataset")
    print("  - Specific data corruption in some images")
    print("  - Long-running process timeout/kill")
    print()

except Exception as e:
    print()
    print("=" * 80)
    print("✗ ERROR DETECTED")
    print("=" * 80)
    print()
    print(f"Error type: {type(e).__name__}")
    print(f"Error message: {e}")
    print()
    print("Full traceback:")
    print("-" * 80)
    import traceback
    traceback.print_exc()
    print()
    sys.exit(1)
