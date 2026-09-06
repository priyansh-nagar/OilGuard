"""
Calculate exact parameter count for the updated lightweight baseline CNN model.
"""
import sys
from pathlib import Path

# Add parent directory to path to import the model
sys.path.insert(0, str(Path(__file__).parent.parent))

from ml.train_baseline import SmallCNN

# Instantiate model
model = SmallCNN()

# Calculate parameters
print("=" * 80)
print("LIGHTWEIGHT CNN PARAMETER COUNT")
print("=" * 80)
print()

total_params = 0
trainable_params = 0

print("Layer-by-layer breakdown:")
print("-" * 80)

for name, param in model.named_parameters():
    layer_params = param.numel()
    total_params += layer_params
    if param.requires_grad:
        trainable_params += layer_params

    print(f"{name:30s}: {layer_params:>10,} {'(trainable)' if param.requires_grad else '(frozen)'}")

print("-" * 80)
print(f"{'TOTAL':30s}: {total_params:>10,} parameters")
print(f"{'TRAINABLE':30s}: {trainable_params:>10,} parameters")
print()

# Architecture summary
print("ARCHITECTURE SUMMARY:")
print("-" * 80)
print("Conv Block 1: 1 → 32 channels, 3×3 kernel, BatchNorm, ReLU, MaxPool")
print("              400×400 → 200×200")
print()
print("Conv Block 2: 32 → 64 channels, 3×3 kernel, BatchNorm, ReLU, MaxPool")
print("              200×200 → 100×100")
print()
print("Conv Block 3: 64 → 128 channels, 3×3 kernel, BatchNorm, ReLU, MaxPool")
print("              100×100 → 50×50")
print()
print("Adaptive Avg Pool: 50×50×128 → 1×1×128 (global pooling)")
print()
print("Flatten: 128 features")
print()
print("FC1: 128 → 64, ReLU, Dropout(0.5)")
print("FC2: 64 → 1 (binary logit)")
print()

# Memory estimate
print("RESOURCE ESTIMATES:")
print("-" * 80)
param_memory_mb = total_params * 4 / (1024**2)
print(f"Model parameters: {param_memory_mb:.2f} MB (float32)")
print(f"Single image (400×400×1): {400*400*4 / (1024**2):.2f} MB (float32)")
print(f"Batch of 32: {32*400*400*4 / (1024**2):.1f} MB")
print()

# Comparison with old architecture
print("IMPROVEMENT OVER ORIGINAL:")
print("-" * 80)
old_params = 82_374_145
reduction = (old_params - total_params) / old_params * 100
print(f"Original architecture: {old_params:,} parameters")
print(f"New architecture:      {total_params:,} parameters")
print(f"Reduction:             {reduction:.1f}% ({old_params // total_params}× smaller)")
print()

# Size assessment
print("CPU TRAINING SUITABILITY:")
print("-" * 80)
if total_params < 500_000:
    print("✓ EXCELLENT - Very lightweight for CPU training")
    print("  Expected training time: 5-15 minutes per epoch on modern CPU")
elif total_params < 1_000_000:
    print("✓ GOOD - Lightweight enough for CPU training")
    print("  Expected training time: 10-20 minutes per epoch on modern CPU")
elif total_params < 5_000_000:
    print("✓ ACCEPTABLE - Should train on CPU in reasonable time")
    print("  Expected training time: 15-30 minutes per epoch on modern CPU")
else:
    print("⚠ May be slow on CPU")

print()
print("=" * 80)
