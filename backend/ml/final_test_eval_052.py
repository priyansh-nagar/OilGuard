import os
import random
import numpy as np
import torch
import torch.nn as nn
from pathlib import Path
from PIL import Image
import pandas as pd

PROJECT_ROOT = Path(r"C:\Users\amit nagar\Projects\oilguard")
CSIRO_ROOT = PROJECT_ROOT / "data" / "CSIRO"
CLASS_0_DIR = CSIRO_ROOT / "S1SAR_UnBalanced_400by400_Class_0"
CLASS_1_DIR = CSIRO_ROOT / "S1SAR_UnBalanced_400by400_Class_1"

BASELINE_MODEL_PATH = PROJECT_ROOT / "backend" / "ml" / "outputs" / "oil_spill_cnn_best.pt"
EXP2_MODEL_PATH = PROJECT_ROOT / "backend" / "ml" / "outputs" / "class_weight_25" / "oil_spill_cnn_best.pt"
OUTPUT_DIR = PROJECT_ROOT / "backend" / "ml" / "outputs" / "threshold_analysis"

RANDOM_SEED = 42
TRAIN_RATIO = 0.70
VAL_RATIO = 0.15
TEST_RATIO = 0.15

DEVICE = torch.device("cpu")
CANDIDATE_THRESHOLD = 0.52

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
def prepare_data():
    class_0_images = list(CLASS_0_DIR.rglob('*.jpg'))
    class_1_images = list(CLASS_1_DIR.rglob('*.jpg'))
    class_0_labels = [0] * len(class_0_images)
    class_1_labels = [1] * len(class_1_images)
    all_images = class_0_images + class_1_images
    all_labels = class_0_labels + class_1_labels
    combined = list(zip(all_images, all_labels))
    random.seed(RANDOM_SEED)
    random.shuffle(combined)
    all_images, all_labels = zip(*combined)
    all_images = list(all_images)
    all_labels = list(all_labels)
    class_0_indices = [i for i, label in enumerate(all_labels) if label == 0]
    class_1_indices = [i for i, label in enumerate(all_labels) if label == 1]
    def split_indices(indices, train_ratio, val_ratio):
        n = len(indices)
        train_end = int(n * train_ratio)
        val_end = train_end + int(n * val_ratio)
        return indices[:train_end], indices[train_end:val_end], indices[val_end:]
    train_0, val_0, test_0 = split_indices(class_0_indices, TRAIN_RATIO, VAL_RATIO)
    train_1, val_1, test_1 = split_indices(class_1_indices, TRAIN_RATIO, VAL_RATIO)
    train_indices = train_0 + train_1
    val_indices = val_0 + val_1
    test_indices = test_0 + test_1
    random.shuffle(train_indices)
    random.shuffle(val_indices)
    random.shuffle(test_indices)
    def get_split(indices):
        return [all_images[i] for i in indices], [all_labels[i] for i in indices]
    train_images, train_labels = get_split(train_indices)
    val_images, val_labels = get_split(val_indices)
    test_images, test_labels = get_split(test_indices)
    return (train_images, train_labels), (val_images, val_labels), (test_images, test_labels)
def predict_prob(model, image_path):
    img = Image.open(image_path).convert('L')
    arr = np.array(img, dtype=np.float32) / 255.0
    t = torch.from_numpy(arr).unsqueeze(0).unsqueeze(0)
    with torch.no_grad():
        logit = model(t)
        return torch.sigmoid(logit).item()
def calculate_metrics(probs, labels, thresh):
    preds = (probs >= thresh).astype(int)
    tp = ((preds == 1) & (labels == 1)).sum()
    tn = ((preds == 0) & (labels == 0)).sum()
    fp = ((preds == 1) & (labels == 0)).sum()
    fn = ((preds == 0) & (labels == 1)).sum()
    accuracy = (tp + tn) / len(labels)
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    from sklearn.metrics import roc_auc_score
    try:
        auc = roc_auc_score(labels, probs)
    except:
        auc = 0.5
    return accuracy, precision, recall, f1, auc, tp, tn, fp, fn
def main():
    print('Loading data...')
    _, _, (test_images, test_labels) = prepare_data()
    labels = np.array(test_labels)
    print('Loading models...')
    model_baseline = SmallCNN().to(DEVICE)
    ckpt_baseline = torch.load(BASELINE_MODEL_PATH, map_location=DEVICE, weights_only=False)
    model_baseline.load_state_dict(ckpt_baseline['model_state_dict'])
    model_baseline.eval()
    model_exp2 = SmallCNN().to(DEVICE)
    ckpt_exp2 = torch.load(EXP2_MODEL_PATH, map_location=DEVICE, weights_only=False)
    model_exp2.load_state_dict(ckpt_exp2['model_state_dict'])
    model_exp2.eval()
    print('Running test inference...')
    probs_baseline = []
    probs_exp2 = []
    for i, path in enumerate(test_images):
        probs_baseline.append(predict_prob(model_baseline, path))
        probs_exp2.append(predict_prob(model_exp2, path))
    probs_baseline = np.array(probs_baseline)
    probs_exp2 = np.array(probs_exp2)
    # Baseline at 0.50
    m_baseline = calculate_metrics(probs_baseline, labels, 0.50)
    # Exp2 at 0.50
    m_exp2_50 = calculate_metrics(probs_exp2, labels, 0.50)
    # Exp2 at candidate 0.52
    m_exp2_52 = calculate_metrics(probs_exp2, labels, CANDIDATE_THRESHOLD)
    # Build CSV rows
    rows = []
    rows.append(['Baseline', 0.50] + [round(x, 4) if isinstance(x, float) else int(x) for x in m_baseline])
    rows.append(['Experiment2', 0.50] + [round(x, 4) if isinstance(x, float) else int(x) for x in m_exp2_50])
    rows.append(['Experiment2', CANDIDATE_THRESHOLD] + [round(x, 4) if isinstance(x, float) else int(x) for x in m_exp2_52])
    df = pd.DataFrame(rows, columns=['Model', 'Threshold', 'Accuracy', 'Precision', 'Recall', 'Oil_F1', 'ROC_AUC', 'TP', 'TN', 'FP', 'FN'])
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = OUTPUT_DIR / 'final_test_threshold_052.csv'
    df.to_csv(csv_path, index=False)
    print(f'CSV saved: {csv_path}')
    # Build Markdown report
    lines = []
    lines.append('# Final Test Evaluation: Experiment 2 (Class Weight 2.5 + Robustness Augmentation)')
    lines.append('')
    lines.append('## Scope')
    lines.append('')
    lines.append('ONE-TIME evaluation on the untouched 847-image test set using frozen candidate deployment threshold 0.52.')
    lines.append('Read-only: no retraining, no model changes, no dataset changes.')
    lines.append('')
    lines.append('## Results')
    lines.append('')
    lines.append('| Model | Threshold | Accuracy | Precision | Recall | Oil F1 | ROC-AUC | TP | TN | FP | FN |')
    lines.append('|-------|-----------|----------|-----------|--------|--------|---------|----|----|----|----|')
    for _, row in df.iterrows():
        m = row['Model']
        t = row['Threshold']
        a = row['Accuracy']
        p = row['Precision']
        r = row['Recall']
        f = row['Oil_F1']
        u = row['ROC_AUC']
        tp = row['TP']
        tn = row['TN']
        fp = row['FP']
        fn = row['FN']
        lines.append(f'| {m} | {t:.2f} | {a:.4f} | {p:.4f} | {r:.4f} | {f:.4f} | {u:.4f} | {tp} | {tn} | {fp} | {fn} |')
    lines.append('')
    lines.append('## Confusion Matrices')
    lines.append('')
    for _, row in df.iterrows():
        m = row['Model']
        tp = row['TP']
        tn = row['TN']
        fp = row['FP']
        fn = row['FN']
        thresh = row['Threshold']
        lines.append(f'### {m} at {thresh:.2f}')
        lines.append('')
        lines.append('| | Pred Non-Oil | Pred Oil |')
        lines.append('|---|---:|---:|')
        lines.append(f'| Actual Non-Oil | {tn} | {fp} |')
        lines.append(f'| Actual Oil | {fn} | {tp} |')
        lines.append('')
    md_path = OUTPUT_DIR / 'final_test_threshold_052.md'
    md_path.write_text('\n'.join(lines), encoding='utf-8')
    print(f'Markdown saved: {md_path}')
    print()
    print('=== FINAL TEST RESULTS ===')
    for _, row in df.iterrows():
        m = row['Model']
        t = row['Threshold']
        a = row['Accuracy']
        p = row['Precision']
        r = row['Recall']
        f = row['Oil_F1']
        u = row['ROC_AUC']
        tp = row['TP']
        tn = row['TN']
        fp = row['FP']
        fn = row['FN']
        print(f'{m} @ {t:.2f}: Acc={a:.4f}, Prec={p:.4f}, Rec={r:.4f}, F1={f:.4f}, AUC={u:.4f}')
        print(f'  CM: TP={tp}, TN={tn}, FP={fp}, FN={fn}')
        print()
if __name__ == '__main__':
    main()
