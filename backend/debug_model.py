"""Controlled verification: test trained model on confirmed Class 0 and Class 1 images"""
import torch
import numpy as np
from PIL import Image
from pathlib import Path

# Import the exact model from detector to ensure identical architecture
import sys
sys.path.insert(0, str(Path(__file__).parent / "app" / "services"))
from detector import SmallCNN, predict_spill

# Model path
MODEL_PATH = Path(__file__).parent / "ml" / "outputs" / "class_weight_25" / "oil_spill_cnn_best.pt"

# Test images - data is at project root, not backend
PROJECT_ROOT = Path(__file__).parent.parent
class0_path = PROJECT_ROOT / "data" / "CSIRO" / "S1SAR_UnBalanced_400by400_Class_0" / "0" / "0_0_0_img_01RNDdyOUhULo97s_SFr_cls_0.jpg"
class1_path = PROJECT_ROOT / "data" / "CSIRO" / "S1SAR_UnBalanced_400by400_Class_1" / "1" / "0_0_0_img_0bBRglmdLdC6cFxF_JAV_cls_1.jpg"

# Load the model checkpoint to get raw logits
ckpt = torch.load(MODEL_PATH, map_location="cpu", weights_only=False)
model = SmallCNN()
model.load_state_dict(ckpt["model_state_dict"])
model.eval()

print(f"Model loaded from: {MODEL_PATH}")
print(f"Checkpoint keys: {list(ckpt.keys())}")
print()

# Test both images
for label, path in [("CLASS_0 (No Oil)", class0_path), ("CLASS_1 (Oil)", class1_path)]:
    print(f"=== {label} ===")
    print(f"Image: {path}")
    print(f"Exists: {path.exists()}")

    # Read image bytes (same as API)
    with open(path, "rb") as f:
        image_bytes = f.read()

    # Run the exact same preprocessing as detector.py
    img = Image.open(path).convert("L")
    arr = np.array(img, dtype=np.float32) / 255.0
    t = torch.from_numpy(arr).unsqueeze(0).unsqueeze(0)

    # Get raw logit
    with torch.no_grad():
        logit = model(t)
        prob = torch.sigmoid(logit).item()

    detected = prob >= 0.52
    confidence = prob if detected else 1.0 - prob

    print(f"Raw logit: {logit.item():.6f}")
    print(f"Sigmoid prob P(oil): {prob:.6f}")
    print(f"Detected (prob >= 0.52): {detected}")
    print(f"Confidence (current logic): {confidence:.6f}")

    # Also run the full API prediction
    result = predict_spill(image_bytes)
    print(f"Full API response:")
    for k, v in result.items():
        print(f"  {k}: {v}")
    print()