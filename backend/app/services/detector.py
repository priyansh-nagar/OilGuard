"""
Real ML spill detector using Experiment 2 model (Class Weight 2.5 + Robustness Augmentation).

Model: backend/ml/outputs/class_weight_25/oil_spill_cnn_best.pt
Threshold: 0.52 (frozen from validation-only analysis)
Preprocessing: JPG → grayscale → float32 → /255.0
"""

import io
import torch
import torch.nn as nn
from pathlib import Path
from PIL import Image
import numpy as np
from datetime import datetime, timezone

# --- Model Architecture (identical to training) ---
class SmallCNN(nn.Module):
    def __init__(self):
        super().__init__()
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

# --- Configuration ---
MODEL_PATH = Path(__file__).resolve().parents[2] / "ml" / "outputs" / "class_weight_25" / "oil_spill_cnn_best.pt"
THRESHOLD = 0.52
DEVICE = torch.device("cpu")
BASE_LAT = 18.95
BASE_LON = 71.85

# --- Lazy model loading ---
_model = None

def _get_model():
    global _model
    if _model is None:
        ckpt = torch.load(MODEL_PATH, map_location=DEVICE, weights_only=False)
        _model = SmallCNN().to(DEVICE)
        _model.load_state_dict(ckpt["model_state_dict"])
        _model.eval()
    return _model

def predict_spill(image_bytes: bytes) -> dict:
    """Run inference on uploaded image bytes. Returns SpillResult dict."""
    model = _get_model()

    # Preprocessing: JPG -> grayscale -> float32 -> /255.0
    img = Image.open(io.BytesIO(image_bytes)).convert("L")
    arr = np.array(img, dtype=np.float32) / 255.0
    t = torch.from_numpy(arr).unsqueeze(0).unsqueeze(0)  # (1, 1, H, W)

    with torch.no_grad():
        logit = model(t)
        prob = torch.sigmoid(logit).item()

    detected = prob >= THRESHOLD
    confidence = float(prob if detected else 1.0 - prob)

    return {
        "detected": bool(detected),
        "confidence": round(confidence, 4),
        "center": {"lat": BASE_LAT, "lon": BASE_LON},
        "estimated_area_km2": 0.0,
        "detection_timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }