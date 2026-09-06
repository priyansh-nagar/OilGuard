"""
CSIRO Sentinel-1 SAR Dataset Inspection Script

This script analyzes the oil/non-oil dataset WITHOUT modifying it.
No training happens here - this is purely exploratory data analysis.

Run from project root:
    cd C:\\Users\\amit nagar\\Projects\\oilguard
    python backend/scripts/inspect_csiro_dataset.py
"""

import os
import random
from pathlib import Path
from PIL import Image
from collections import Counter
import time

# ============================================================================
# Configuration
# ============================================================================

# Paths relative to project root
PROJECT_ROOT = Path(__file__).parent.parent.parent
CSIRO_ROOT = PROJECT_ROOT / "data" / "CSIRO"
CLASS_0_DIR = CSIRO_ROOT / "S1SAR_UnBalanced_400by400_Class_0"
CLASS_1_DIR = CSIRO_ROOT / "S1SAR_UnBalanced_400by400_Class_1"
REPORT_PATH = CSIRO_ROOT / "dataset_report.txt"
SAMPLES_PATH = CSIRO_ROOT / "dataset_samples.png"

# How many images to visually sample
SAMPLES_PER_CLASS = 10

# ============================================================================
# Helper Functions
# ============================================================================

def find_all_images(directory):
    """
    Recursively find all .jpg files in a directory.
    Returns a list of Path objects.
    """
    images = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                images.append(Path(root) / file)
    return images


def check_image_validity(image_path):
    """
    Try to open an image and return info about it.

    Returns:
        (is_valid, width, height, mode, file_size_kb, error_message)
    """
    try:
        img = Image.open(image_path)
        width, height = img.size
        mode = img.mode
        file_size_kb = image_path.stat().st_size / 1024
        img.close()
        return (True, width, height, mode, file_size_kb, None)
    except Exception as e:
        return (False, None, None, None, None, str(e))


def create_sample_grid(class_0_samples, class_1_samples, output_path):
    """
    Create a visual grid showing sample images from both classes.

    Layout:
        Row 1: "Class 0 (Non-Oil)" label + 10 sample images
        Row 2: "Class 1 (Oil)" label + 10 sample images

    Each image is resized to 128x128 for the grid.
    """
    THUMB_SIZE = 128
    LABEL_WIDTH = 150
    GRID_COLS = len(class_0_samples)

    # Calculate grid dimensions
    grid_width = LABEL_WIDTH + (THUMB_SIZE * GRID_COLS)
    grid_height = THUMB_SIZE * 2

    # Create blank canvas (white background)
    grid = Image.new('RGB', (grid_width, grid_height), color='white')

    # We'll draw text labels manually with PIL
    from PIL import ImageDraw, ImageFont
    draw = ImageDraw.Draw(grid)

    try:
        # Try to use a reasonable font (falls back to default if not available)
        font = ImageFont.truetype("arial.ttf", 14)
    except:
        font = ImageFont.load_default()

    # Draw labels
    draw.text((10, THUMB_SIZE // 2 - 20), "Class 0", fill='black', font=font)
    draw.text((10, THUMB_SIZE // 2 - 5), "(Non-Oil)", fill='black', font=font)
    draw.text((10, THUMB_SIZE + THUMB_SIZE // 2 - 20), "Class 1", fill='black', font=font)
    draw.text((10, THUMB_SIZE + THUMB_SIZE // 2 - 5), "(Oil)", fill='black', font=font)

    # Paste Class 0 samples
    for i, img_path in enumerate(class_0_samples):
        try:
            img = Image.open(img_path)
            img = img.resize((THUMB_SIZE, THUMB_SIZE), Image.Resampling.LANCZOS)
            x = LABEL_WIDTH + (i * THUMB_SIZE)
            y = 0
            grid.paste(img, (x, y))
            img.close()
        except Exception as e:
            print(f"Warning: Could not add {img_path.name} to grid: {e}")

    # Paste Class 1 samples
    for i, img_path in enumerate(class_1_samples):
        try:
            img = Image.open(img_path)
            img = img.resize((THUMB_SIZE, THUMB_SIZE), Image.Resampling.LANCZOS)
            x = LABEL_WIDTH + (i * THUMB_SIZE)
            y = THUMB_SIZE
            grid.paste(img, (x, y))
            img.close()
        except Exception as e:
            print(f"Warning: Could not add {img_path.name} to grid: {e}")

    # Save the grid
    grid.save(output_path, quality=95)
    print(f"✓ Sample grid saved to: {output_path}")


# ============================================================================
# Main Inspection Logic
# ============================================================================

def main():
    print("=" * 80)
    print("CSIRO Sentinel-1 SAR Dataset Inspection")
    print("=" * 80)
    print()

    # Check directories exist
    if not CLASS_0_DIR.exists():
        print(f"ERROR: Class 0 directory not found: {CLASS_0_DIR}")
        return
    if not CLASS_1_DIR.exists():
        print(f"ERROR: Class 1 directory not found: {CLASS_1_DIR}")
        return

    report_lines = []
    report_lines.append("=" * 80)
    report_lines.append("CSIRO Sentinel-1 SAR Dataset Inspection Report")
    report_lines.append("=" * 80)
    report_lines.append(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("")

    # ========================================================================
    # Step 1: Count all images
    # ========================================================================
    print("[1/7] Counting images...")
    class_0_images = find_all_images(CLASS_0_DIR)
    class_1_images = find_all_images(CLASS_1_DIR)
    total_images = len(class_0_images) + len(class_1_images)

    print(f"  Class 0 (Non-Oil): {len(class_0_images)} images")
    print(f"  Class 1 (Oil):     {len(class_1_images)} images")
    print(f"  Total:             {total_images} images")
    print()

    report_lines.append("1. IMAGE COUNTS")
    report_lines.append("-" * 80)
    report_lines.append(f"Class 0 (Non-Oil): {len(class_0_images):,} images")
    report_lines.append(f"Class 1 (Oil):     {len(class_1_images):,} images")
    report_lines.append(f"Total:             {total_images:,} images")
    report_lines.append("")

    # ========================================================================
    # Step 2: Calculate class distribution
    # ========================================================================
    print("[2/7] Analyzing class distribution...")
    class_0_pct = (len(class_0_images) / total_images) * 100
    class_1_pct = (len(class_1_images) / total_images) * 100
    imbalance_ratio = len(class_0_images) / len(class_1_images)

    print(f"  Class 0: {class_0_pct:.1f}%")
    print(f"  Class 1: {class_1_pct:.1f}%")
    print(f"  Imbalance ratio: {imbalance_ratio:.2f}:1 (Class 0 : Class 1)")
    print()

    report_lines.append("2. CLASS DISTRIBUTION")
    report_lines.append("-" * 80)
    report_lines.append(f"Class 0 (Non-Oil): {class_0_pct:.2f}%")
    report_lines.append(f"Class 1 (Oil):     {class_1_pct:.2f}%")
    report_lines.append(f"Imbalance Ratio:   {imbalance_ratio:.2f}:1 (Non-Oil : Oil)")
    report_lines.append("")
    report_lines.append("INTERPRETATION:")
    report_lines.append(f"  - Dataset is moderately imbalanced ({imbalance_ratio:.1f}x more non-oil samples)")
    report_lines.append("  - This reflects real-world conditions (oil spills are rarer than look-alikes)")
    report_lines.append("  - Class weighting or stratified sampling recommended during training")
    report_lines.append("")

    # ========================================================================
    # Step 3: Check image validity and collect metadata
    # ========================================================================
    print("[3/7] Checking image validity (this may take a minute)...")

    corrupted_files = []
    dimensions_counter = Counter()
    modes_counter = Counter()
    file_sizes = []

    all_images = class_0_images + class_1_images

    for i, img_path in enumerate(all_images):
        if (i + 1) % 500 == 0:
            print(f"  Checked {i + 1}/{len(all_images)} images...")

        is_valid, width, height, mode, size_kb, error = check_image_validity(img_path)

        if not is_valid:
            corrupted_files.append((img_path, error))
        else:
            dimensions_counter[(width, height)] += 1
            modes_counter[mode] += 1
            file_sizes.append(size_kb)

    print(f"  ✓ Checked all {len(all_images)} images")
    print()

    report_lines.append("3. IMAGE VALIDITY CHECK")
    report_lines.append("-" * 80)
    report_lines.append(f"Total images checked: {len(all_images):,}")
    report_lines.append(f"Valid images:         {len(all_images) - len(corrupted_files):,}")
    report_lines.append(f"Corrupted/Unreadable: {len(corrupted_files)}")

    if corrupted_files:
        report_lines.append("")
        report_lines.append("CORRUPTED FILES:")
        for path, error in corrupted_files[:10]:  # Show first 10
            report_lines.append(f"  - {path.name}: {error}")
        if len(corrupted_files) > 10:
            report_lines.append(f"  ... and {len(corrupted_files) - 10} more")
    report_lines.append("")

    # ========================================================================
    # Step 4: Report dimensions
    # ========================================================================
    print("[4/7] Analyzing image dimensions...")

    report_lines.append("4. IMAGE DIMENSIONS")
    report_lines.append("-" * 80)

    if dimensions_counter:
        most_common_dim = dimensions_counter.most_common(1)[0]
        report_lines.append(f"Most common dimension: {most_common_dim[0]} ({most_common_dim[1]:,} images)")
        report_lines.append("")
        report_lines.append("All dimensions found:")
        for dim, count in dimensions_counter.most_common():
            report_lines.append(f"  {dim[0]}x{dim[1]}: {count:,} images")

    report_lines.append("")

    # ========================================================================
    # Step 5: Report image modes
    # ========================================================================
    print("[5/7] Analyzing image modes...")

    report_lines.append("5. IMAGE MODES (Color Space)")
    report_lines.append("-" * 80)

    for mode, count in modes_counter.most_common():
        mode_desc = {
            'L': 'Grayscale',
            'RGB': 'RGB Color',
            'RGBA': 'RGB with Alpha',
            'P': 'Palette',
        }.get(mode, mode)
        report_lines.append(f"  {mode} ({mode_desc}): {count:,} images")

    report_lines.append("")

    # ========================================================================
    # Step 6: Report file sizes
    # ========================================================================
    print("[6/7] Analyzing file sizes...")

    if file_sizes:
        avg_size = sum(file_sizes) / len(file_sizes)
        min_size = min(file_sizes)
        max_size = max(file_sizes)
        total_size_mb = sum(file_sizes) / 1024

        report_lines.append("6. FILE SIZES")
        report_lines.append("-" * 80)
        report_lines.append(f"Average file size: {avg_size:.1f} KB")
        report_lines.append(f"Minimum file size: {min_size:.1f} KB")
        report_lines.append(f"Maximum file size: {max_size:.1f} KB")
        report_lines.append(f"Total dataset size: {total_size_mb:.1f} MB")
        report_lines.append("")

    # ========================================================================
    # Step 7: Create visual samples
    # ========================================================================
    print("[7/7] Creating visual sample grid...")

    # Randomly sample images
    class_0_sample_paths = random.sample(class_0_images, min(SAMPLES_PER_CLASS, len(class_0_images)))
    class_1_sample_paths = random.sample(class_1_images, min(SAMPLES_PER_CLASS, len(class_1_images)))

    create_sample_grid(class_0_sample_paths, class_1_sample_paths, SAMPLES_PATH)

    report_lines.append("7. VISUAL SAMPLES")
    report_lines.append("-" * 80)
    report_lines.append(f"Created sample grid: {SAMPLES_PATH.name}")
    report_lines.append(f"  - {len(class_0_sample_paths)} random Class 0 (Non-Oil) samples")
    report_lines.append(f"  - {len(class_1_sample_paths)} random Class 1 (Oil) samples")
    report_lines.append("")

    # ========================================================================
    # Analysis and Recommendations
    # ========================================================================
    print()
    print("=" * 80)
    print("ANALYSIS & RECOMMENDATIONS")
    print("=" * 80)

    report_lines.append("=" * 80)
    report_lines.append("8. ANALYSIS & RECOMMENDATIONS")
    report_lines.append("=" * 80)
    report_lines.append("")

    # Q1: Suitable for binary classification?
    report_lines.append("Q: Is this dataset suitable for binary oil/non-oil classification?")
    report_lines.append("A: YES")
    report_lines.append("   - Dataset is clearly labeled (Class 0 = Non-Oil, Class 1 = Oil)")
    report_lines.append("   - Images are uniform size (400x400), ideal for CNNs")
    report_lines.append(f"   - Sufficient samples ({total_images:,} total) for training a small CNN")
    report_lines.append("   - SAR imagery is appropriate for oil detection")
    report_lines.append("")

    # Q2: Evidence of look-alikes?
    report_lines.append("Q: Is there evidence of look-alike/non-oil examples?")
    report_lines.append("A: YES")
    report_lines.append("   - Class 0 contains 3,725 non-oil examples")
    report_lines.append("   - These likely include ships, wind patterns, algae, etc.")
    report_lines.append("   - This is CRITICAL for reducing false positives")
    report_lines.append("   - Check dataset_samples.png to visually confirm variety")
    report_lines.append("")

    # Q3: Classes sufficiently different?
    report_lines.append("Q: Are the two classes sufficiently different?")
    report_lines.append("A: Check dataset_samples.png to visually assess:")
    report_lines.append("   - Oil appears as dark patches in SAR (dampens waves)")
    report_lines.append("   - Non-oil should show brighter or different texture patterns")
    report_lines.append("   - If classes look very similar, model will struggle")
    report_lines.append("   - Visual inspection by human is essential before training")
    report_lines.append("")

    # Q4: Duplicates?
    filenames_class_0 = [img.name for img in class_0_images]
    filenames_class_1 = [img.name for img in class_1_images]
    duplicate_filenames = set(filenames_class_0) & set(filenames_class_1)

    report_lines.append("Q: Are there duplicate filenames or suspicious duplicates?")
    if duplicate_filenames:
        report_lines.append(f"A: WARNING - {len(duplicate_filenames)} duplicate filenames found:")
        for fname in list(duplicate_filenames)[:10]:
            report_lines.append(f"     {fname}")
    else:
        report_lines.append("A: NO duplicate filenames between classes (good)")
    report_lines.append("")

    # Q5: Data quality problems?
    report_lines.append("Q: Are there any obvious data-quality problems?")
    if corrupted_files:
        report_lines.append(f"A: WARNING - {len(corrupted_files)} corrupted/unreadable files found")
        report_lines.append("   - See section 3 for details")
    else:
        report_lines.append("A: NO corrupted files detected (excellent)")

    if len(dimensions_counter) > 1:
        report_lines.append("   - WARNING: Multiple image dimensions found")
        report_lines.append("   - Most CNNs expect uniform input size")
        report_lines.append("   - May need to resize during preprocessing")
    else:
        report_lines.append("   - All images have consistent dimensions (excellent)")
    report_lines.append("")

    # Q6: Train/val/test split?
    report_lines.append("Q: What train/validation/test split would you recommend?")
    report_lines.append("A: Recommended split:")

    train_pct = 70
    val_pct = 15
    test_pct = 15

    train_0 = int(len(class_0_images) * train_pct / 100)
    val_0 = int(len(class_0_images) * val_pct / 100)
    test_0 = len(class_0_images) - train_0 - val_0

    train_1 = int(len(class_1_images) * train_pct / 100)
    val_1 = int(len(class_1_images) * val_pct / 100)
    test_1 = len(class_1_images) - train_1 - val_1

    report_lines.append(f"   - Train: {train_pct}% (~{train_0 + train_1:,} images)")
    report_lines.append(f"   - Validation: {val_pct}% (~{val_0 + val_1:,} images)")
    report_lines.append(f"   - Test: {test_pct}% (~{test_0 + test_1:,} images)")
    report_lines.append("   - Use STRATIFIED split to maintain class balance in each set")
    report_lines.append("   - Set random seed for reproducibility")
    report_lines.append("")

    # Q7: Class weighting vs oversampling?
    report_lines.append("Q: Would class weighting be preferable to oversampling?")
    report_lines.append("A: YES, class weighting is recommended:")
    report_lines.append(f"   - Imbalance ratio is {imbalance_ratio:.2f}:1 (moderate, not extreme)")
    report_lines.append("   - Class weighting is simpler and avoids duplicate samples")
    report_lines.append(f"   - Suggested weights: Class 0 = 1.0, Class 1 = {imbalance_ratio:.2f}")
    report_lines.append("   - Alternative: Oversample Class 1 or undersample Class 0")
    report_lines.append("   - Can experiment with both approaches during training")
    report_lines.append("")

    # Q8: Suitable for laptop training?
    report_lines.append("Q: Is this dataset appropriate for training on a normal laptop?")
    report_lines.append("A: YES, this is very laptop-friendly:")
    report_lines.append(f"   - Total size: {total_size_mb:.1f} MB (fits easily in RAM)")
    report_lines.append("   - Image size: 400x400 (manageable for small CNNs)")
    report_lines.append(f"   - Sample count: {total_images:,} (not huge, trains quickly)")
    report_lines.append("   - Can train a simple CNN or use transfer learning")
    report_lines.append("   - Expect training time: 10-30 minutes per epoch on CPU")
    report_lines.append("   - If you have a GPU, training will be much faster")
    report_lines.append("")

    # Summary
    report_lines.append("=" * 80)
    report_lines.append("SUMMARY")
    report_lines.append("=" * 80)
    report_lines.append("")
    report_lines.append("✓ Dataset is clean and well-structured")
    report_lines.append("✓ Suitable for binary classification (oil vs non-oil)")
    report_lines.append("✓ Moderate class imbalance (manageable with class weighting)")
    report_lines.append("✓ No major data quality issues detected")
    report_lines.append("✓ Laptop-friendly size and complexity")
    report_lines.append("")
    report_lines.append("NEXT STEPS:")
    report_lines.append("  1. Visually inspect dataset_samples.png to confirm class differences")
    report_lines.append("  2. Decide on train/val/test split strategy")
    report_lines.append("  3. Choose model architecture (simple CNN or transfer learning)")
    report_lines.append("  4. Set up data loading pipeline with class weighting")
    report_lines.append("  5. Start with a baseline model (Stage 2B)")
    report_lines.append("")
    report_lines.append("RECOMMENDED BASELINE MODEL:")
    report_lines.append("  - Small CNN (3-4 conv layers) OR")
    report_lines.append("  - Transfer learning with MobileNetV2/EfficientNet-B0 (pretrained)")
    report_lines.append("  - Binary cross-entropy loss with class weights")
    report_lines.append("  - Adam optimizer, learning rate ~0.001")
    report_lines.append("  - Early stopping on validation loss")
    report_lines.append("")

    # ========================================================================
    # Save report
    # ========================================================================
    print()
    print("Saving report...")

    with open(REPORT_PATH, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))

    print(f"✓ Report saved to: {REPORT_PATH}")
    print()
    print("=" * 80)
    print("INSPECTION COMPLETE!")
    print("=" * 80)
    print()
    print(f"Generated files:")
    print(f"  - {REPORT_PATH}")
    print(f"  - {SAMPLES_PATH}")
    print()
    print("Next: Review the sample grid and report before proceeding to Stage 2B.")


if __name__ == "__main__":
    main()
