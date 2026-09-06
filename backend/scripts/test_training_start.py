"""
Test script to diagnose training crash.
Tests data loading, model creation, and first forward pass.
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

print("=" * 80)
print("DIAGNOSTIC TEST FOR TRAINING CRASH")
print("=" * 80)
print()

try:
    print("[1/6] Importing modules...")
    from backend.ml.train_baseline import (
        SmallCNN,
        OilSpillDataset,
        CLASS_0_DIR,
        CLASS_1_DIR,
        DEVICE,
    )
    import torch
    import torch.nn as nn
    from torch.utils.data import DataLoader
    print("✓ Imports successful")
    print()

    print("[2/6] Loading small sample of images...")
    class_0_images = list(CLASS_0_DIR.rglob("*.jpg"))[:10]
    class_1_images = list(CLASS_1_DIR.rglob("*.jpg"))[:10]
    print(f"  Class 0: {len(class_0_images)} images")
    print(f"  Class 1: {len(class_1_images)} images")
    print()

    print("[3/6] Creating dataset...")
    all_images = class_0_images + class_1_images
    all_labels = [0] * len(class_0_images) + [1] * len(class_1_images)
    dataset = OilSpillDataset(all_images, all_labels)
    print(f"✓ Dataset created: {len(dataset)} samples")
    print()

    print("[4/6] Creating data loader...")
    loader = DataLoader(dataset, batch_size=4, shuffle=False)
    print(f"✓ DataLoader created: {len(loader)} batches")
    print()

    print("[5/6] Creating model...")
    model = SmallCNN().to(DEVICE)
    print(f"✓ Model created on device: {DEVICE}")
    print(f"  Parameters: {sum(p.numel() for p in model.parameters()):,}")
    print()

    print("[6/6] Testing forward pass...")
    model.eval()
    with torch.no_grad():
        for batch_idx, (images, labels) in enumerate(loader):
            print(f"  Batch {batch_idx + 1}/{len(loader)}")
            print(f"    Images shape: {images.shape}")
            print(f"    Labels: {labels.tolist()}")

            images = images.to(DEVICE)
            labels = labels.to(DEVICE)

            outputs = model(images)
            print(f"    Outputs shape: {outputs.shape}")
            print(f"    Outputs: {outputs.squeeze().tolist()}")

            if batch_idx >= 2:  # Test first 3 batches
                break

    print()
    print("=" * 80)
    print("✓ ALL TESTS PASSED")
    print("=" * 80)
    print()
    print("Data loading and model forward pass work correctly.")
    print("The crash must be happening during training loop or optimization.")

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
