import sys
sys.path.insert(0, r'C:\Users\amit nagar\Projects\oilguard\backend')

import torch
import io
from PIL import Image
import numpy as np
from pathlib import Path

# Model path
MODEL_PATH = Path(r'C:\Users\amit nagar\Projects\oilguard\backend\ml\outputs\class_weight_25\oil_spill_cnn_best.pt')

# Load model
ckpt = torch.load(MODEL_PATH, map_location='cpu', weights_only=False)

class SmallCNN(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = torch.nn.Conv2d(1, 32, kernel_size=3, padding=1)
        self.bn1 = torch.nn.BatchNorm2d(32)
        self.conv2 = torch.nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.bn2 = torch.nn.BatchNorm2d(64)
        self.conv3 = torch.nn.Conv2d(64, 128, kernel_size=3, padding=1)
        self.bn3 = torch.nn.BatchNorm2d(128)
        self.pool = torch.nn.MaxPool2d(2, 2)
        self.relu = torch.nn.ReLU()
        self.adaptive_pool = torch.nn.AdaptiveAvgPool2d((1, 1))
        self.fc1 = torch.nn.Linear(128, 64)
        self.dropout = torch.nn.Dropout(0.5)
        self.fc2 = torch.nn.Linear(64, 1)

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

model = SmallCNN().to('cpu')
model.load_state_dict(ckpt['model_state_dict'])
model.eval()

THRESHOLD = 0.52

# Get 5 Class 0 images
class0_dir = Path(r'C:\Users\amit nagar\Projects\oilguard\data\CSIRO\S1SAR_UnBalanced_400by400_Class_0\0')
class0_files = list(class0_dir.glob('*.jpg'))[:5]

# Get 1 Class 1 image
class1_dir = Path(r'C:\Users\amit nagar\Projects\oilguard\data\CSIRO\S1SAR_UnBalanced_400by400_Class_1\1')
class1_files = list(class1_dir.glob('*.jpg'))[:1]

print('=' * 80)
print('CLASS 0 IMAGES (Non-Oil)')
print('=' * 80)

for i, f in enumerate(class0_files):
    img = Image.open(f).convert('L')
    arr = np.array(img, dtype=np.float32) / 255.0
    t = torch.from_numpy(arr).unsqueeze(0).unsqueeze(0)

    with torch.no_grad():
        logit = model(t)
        prob = torch.sigmoid(logit).item()

    detected = prob >= THRESHOLD
    confidence = float(prob if detected else 1.0 - prob)

    print(f'\nImage {i+1}: {f.name}')
    print(f'  Raw logit: {logit.item():.6f}')
    print(f'  P(Oil):    {prob:.6f}')
    print(f'  Threshold: {THRESHOLD}')
    print(f'  Detected:  {detected}')
    print(f'  Confidence: {confidence:.4f}')

print('\n' + '=' * 80)
print('CLASS 1 IMAGE (Oil) - CONTROL')
print('=' * 80)

for i, f in enumerate(class1_files):
    img = Image.open(f).convert('L')
    arr = np.array(img, dtype=np.float32) / 255.0
    t = torch.from_numpy(arr).unsqueeze(0).unsqueeze(0)

    with torch.no_grad():
        logit = model(t)
        prob = torch.sigmoid(logit).item()

    detected = prob >= THRESHOLD
    confidence = float(prob if detected else 1.0 - prob)

    print(f'\nImage {i+1}: {f.name}')
    print(f'  Raw logit: {logit.item():.6f}')
    print(f'  P(Oil):    {prob:.6f}')
    print(f'  Threshold: {THRESHOLD}')
    print(f'  Detected:  {detected}')
    print(f'  Confidence: {confidence:.4f}')

# Summary
class0_detected = sum(1 for f in class0_files if True)
class0_not_detected = 0
# We'll recalculate
print('\n' + '=' * 80)
print('SUMMARY')
print('=' * 80)