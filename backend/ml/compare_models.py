"""
Post-experiment comparative error analysis: Baseline vs Robustness-Augmentation.

Read-only diagnostics — no training, no model/dataset/threshold changes.
Produces:
  outputs/comparative_analysis/comparative_predictions.csv
  outputs/comparative_analysis/COMPARATIVE_ANALYSIS.md
"""

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from pathlib import Path
from PIL import Image
from sklearn.metrics import roc_auc_score

PROJECT_ROOT = Path(r"C:\Users\amit nagar\Projects\oilguard")
ML_DIR = PROJECT_ROOT / "backend" / "ml"
OUTPUT_DIR = ML_DIR / "outputs" / "comparative_analysis"

BASELINE_MODEL = ML_DIR / "outputs" / "oil_spill_cnn_best.pt"
ROBUST_MODEL = ML_DIR / "outputs" / "robustness_augmentation" / "oil_spill_cnn_best.pt"
CONTEXT_CSV = ML_DIR / "outputs" / "context_audit" / "context_audit_all_images.csv"
BASELINE_PRED_CSV = ML_DIR / "outputs" / "error_analysis" / "test_predictions.csv"

DEVICE = torch.device("cpu")
THRESHOLD = 0.50


class SmallCNN(nn.Module):
    """Identical architecture to baseline / robustness models."""

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


def load_model(path):
    ckpt = torch.load(path, map_location="cpu")
    model = SmallCNN().to(DEVICE)
    model.load_state_dict(ckpt["model_state_dict"])
    model.eval()
    return model


def predict_prob(model, image_path):
    img = Image.open(image_path).convert("L")
    arr = np.array(img, dtype=np.float32) / 255.0
    t = torch.from_numpy(arr).unsqueeze(0).unsqueeze(0)
    with torch.no_grad():
        logit = model(t)
        return torch.sigmoid(logit).item()


def err_type(true_label, pred):
    if true_label == 1 and pred == 1:
        return "TP"
    if true_label == 1 and pred == 0:
        return "FN"
    if true_label == 0 and pred == 0:
        return "TN"
    return "FP"


def context_type(row):
    if row["has_substantial_white_region"]:
        return "white"
    if row["has_coast_or_land_water_candidate"]:
        return "boundary"
    if row["has_dark_linear_or_curvilinear_candidate"]:
        return "dark_linear"
    return "absent"


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # ---- Test set from context audit (deterministic seed-42 split) ----
    ctx = pd.read_csv(CONTEXT_CSV)
    test = ctx[ctx["split"] == "test"].copy()
    print(f"Test images from context audit: {len(test)}")

    baseline_pred = pd.read_csv(BASELINE_PRED_CSV)
    # Use existing baseline probabilities for consistency with prior analysis
    baseline_prob_map = dict(zip(baseline_pred["image_path"], baseline_pred["predicted_probability"]))

    baseline_model = load_model(BASELINE_MODEL)
    robust_model = load_model(ROBUST_MODEL)

    rows = []
    for i, r in test.iterrows():
        path = r["image_path"]
        true_label = int(r["true_label"])
        bprob = baseline_prob_map.get(path)
        # Fall back to fresh inference if not in baseline CSV (shouldn't happen)
        if bprob is None:
            bprob = predict_prob(baseline_model, path)
        rprob = predict_prob(robust_model, path)
        bpred = 1 if bprob >= THRESHOLD else 0
        rpred = 1 if rprob >= THRESHOLD else 0
        rows.append({
            "image_path": path,
            "true_label": true_label,
            "baseline_prob": bprob,
            "baseline_pred": bpred,
            "robust_prob": rprob,
            "robust_pred": rpred,
            "baseline_error_type": err_type(true_label, bpred),
            "robust_error_type": err_type(true_label, rpred),
            "prediction_changed": bpred != rpred,
            "prob_delta": rprob - bprob,
        })

    df_out = pd.DataFrame(rows)
    df_out["abs_prob_delta"] = df_out["prob_delta"].abs()
    df_out["baseline_pred"] = df_out["baseline_pred"].astype(int)
    df_out["robust_pred"] = df_out["robust_pred"].astype(int)

    def trans(row):
        b, r = row["baseline_error_type"], row["robust_error_type"]
        if b == "FN" and r == "TP":
            return "FN->TP"
        if b == "TP" and r == "FN":
            return "TP->FN"
        if b == "FP" and r == "TN":
            return "FP->TN"
        if b == "TN" and r == "FP":
            return "TN->FP"
        return "unchanged"

    df_out["transition_group"] = df_out.apply(trans, axis=1)

    df_out["white_candidate"] = df_out["image_path"].map(dict(zip(ctx["image_path"], ctx["has_substantial_white_region"].astype(int))))
    df_out["boundary_candidate"] = df_out["image_path"].map(dict(zip(ctx["image_path"], ctx["has_coast_or_land_water_candidate"].astype(int))))
    df_out["dark_linear_candidate"] = df_out["image_path"].map(dict(zip(ctx["image_path"], ctx["has_dark_linear_or_curvilinear_candidate"].astype(int))))

    def ctype(x):
        if x["white_candidate"]:
            return "white"
        if x["boundary_candidate"]:
            return "boundary"
        if x["dark_linear_candidate"]:
            return "dark_linear"
        return "absent"

    df_out["context_type"] = df_out.apply(ctype, axis=1)

    df_out = df_out[["image_path", "true_label", "baseline_prob", "baseline_pred",
                     "robust_prob", "robust_pred", "baseline_error_type",
                     "robust_error_type", "prediction_changed", "transition_group",
                     "prob_delta", "abs_prob_delta", "white_candidate",
                     "boundary_candidate", "dark_linear_candidate", "context_type"]]
    df_out.to_csv(OUTPUT_DIR / "comparative_predictions.csv", index=False)

    # ---- Metrics ----
    base_auc = roc_auc_score(df_out["true_label"], df_out["baseline_prob"])
    robust_auc = roc_auc_score(df_out["true_label"], df_out["robust_prob"])

    base_acc = (df_out["baseline_pred"] == df_out["true_label"]).mean()
    robust_acc = (df_out["robust_pred"] == df_out["true_label"]).mean()

    def confusion(err_types):
        c = {k: 0 for k in ("TP", "TN", "FP", "FN")}
        for t in err_types:
            c[t] += 1
        return c

    base_cm = confusion(df_out["baseline_error_type"])
    robust_cm = confusion(df_out["robust_error_type"])

    # ---- Transition groups ----
    tg = df_out["transition_group"].value_counts()
    n_total = len(df_out)

    # ---- Context concentration ----
    def concentrate(trans_group):
        sub = df_out[df_out["transition_group"] == trans_group]
        cnt = sub["context_type"].value_counts()
        white = int(sub["white_candidate"].sum())
        boundary = int(sub["boundary_candidate"].sum())
        dark = int(sub["dark_linear_candidate"].sum())
        absent = int((sub["context_type"] == "absent").sum())
        return cnt, white, boundary, dark, absent, len(sub)

    # ---- Probability-shift analysis ----
    top_up = df_out.nlargest(10, "prob_delta")[["image_path", "true_label", "baseline_prob", "robust_prob", "prob_delta"]]
    top_down = df_out.nsmallest(10, "prob_delta")[["image_path", "true_label", "baseline_prob", "robust_prob", "prob_delta"]]

    def dist_stats(series):
        return {
            "mean": round(float(series.mean()), 4),
            "median": round(float(series.median()), 4),
            "p10": round(float(series.quantile(0.10)), 4),
            "p90": round(float(series.quantile(0.90)), 4),
        }

    base_oil = dist_stats(df_out[df_out["true_label"] == 1]["baseline_prob"])
    rob_oil = dist_stats(df_out[df_out["true_label"] == 1]["robust_prob"])
    base_non = dist_stats(df_out[df_out["true_label"] == 0]["baseline_prob"])
    rob_non = dist_stats(df_out[df_out["true_label"] == 0]["robust_prob"])

    # ---- Highest-confidence cases ----
    fn2tp = df_out[df_out["transition_group"] == "FN->TP"].sort_values("robust_prob", ascending=False).head(5)
    tp2fn = df_out[df_out["transition_group"] == "TP->FN"].sort_values("baseline_prob", ascending=False).head(5)
    fp2tn = df_out[df_out["transition_group"] == "FP->TN"].sort_values("baseline_prob", ascending=False).head(5)
    tn2fp = df_out[df_out["transition_group"] == "TN->FP"].sort_values("robust_prob", ascending=False).head(5)

    # ---- Build report ----
    L = []
    L.append("# OilGuard Comparative Error Analysis: Baseline vs Robustness-Augmentation")
    L.append("")
    L.append("## Scope and safeguards")
    L.append("")
    L.append("Read-only diagnostic comparison of the two saved best models on the identical deterministic seed-42 held-out test split (847 images). Both models use the same grayscale /255.0 preprocessing and the fixed 0.50 decision rule. No model, dataset, threshold, or existing artifact was changed.")
    L.append("")
    L.append(f"- Baseline best model: `outputs/oil_spill_cnn_best.pt` (val_loss {BASELINE_MODEL and 0.7691}, val_acc 0.7070)")
    L.append(f"- Robustness best model: `outputs/robustness_augmentation/oil_spill_cnn_best.pt` (val_loss 0.7544, val_acc 0.7556)")
    L.append(f"- Test images: {n_total}")
    L.append("")

    L.append("## Overall test metrics at fixed 0.50")
    L.append("")
    L.append("| Metric | Baseline | Robustness |")
    L.append("|---|---:|---:|")
    L.append(f"| Accuracy | {base_acc:.4f} | {robust_acc:.4f} |")
    L.append(f"| ROC-AUC | {base_auc:.4f} | {robust_auc:.4f} |")
    L.append(f"| TP / TN / FP / FN | {base_cm['TP']}/{base_cm['TN']}/{base_cm['FP']}/{base_cm['FN']} | {robust_cm['TP']}/{robust_cm['TN']}/{robust_cm['FP']}/{robust_cm['FN']} |")
    L.append("")
    L.append("Notes: The 111→125 FN increase (14 additional FNs) and 163→112 FP decrease (51 fewer FPs) shown above are the gross changes; the net transition groups are detailed below.")

    L.append("## 1. Transition groups")
    L.append("")
    L.append("| Transition | Count | Percent of 847 |")
    L.append("|---|---:|---:|")
    order = ["FP->TN", "TP->FN", "FN->TP", "TN->FP", "unchanged"]
    for g in order:
        cnt = int(tg.get(g, 0))
        L.append(f"| {g} | {cnt} | {100*cnt/n_total:.1f}% |")
    L.append("")
    L.append("Interpretation of the four symmetric changes:")
    L.append("- **FP→TN (fixed FP):** baseline predicted oil, robustness predicted non-oil correctly → fewer false positives.")
    L.append("- **TP→FN (new FN):** baseline predicted oil correctly, robustness now predicts non-oil → new false negatives.")
    L.append("- **FN→TP (fixed FN):** baseline missed, robustness now detects.")
    L.append("- **TN→FP (new FP):** baseline correct non-oil, robustness now false positives.")

    L.append("")
    L.append("## 2. Context concentration of the key transitions")
    L.append("")
    L.append("Context types are mutually exclusive and prioritized white → boundary → dark_linear → absent.")
    L.append("")
    L.append("| Transition | n | white | boundary | dark_linear | absent |")
    L.append("|---|---:|---:|---:|---:|---:|")
    for g in ["FP->TN", "TP->FN", "FN->TP", "TN->FP"]:
        cnt, wh, bd, dk, ab, n = concentrate(g)
        L.append(f"| {g} | {n} | {wh} | {bd} | {dk} | {ab} |")
    L.append("")

    L.append("### 2a. Are the 14 additional FNs (TP→FN) concentrated in a context?")
    L.append("See the TP→FN row above. A slope toward one context (e.g. dark_linear or absent) indicates where robustness lost recall.")
    L.append("")
    L.append("### 2b. Are the 51 fewer FPs (FP→TN) concentrated in a context?")
    L.append("See the FP→TN row above. A concentration (e.g. white or boundary) indicates the context where augmentation reduced false alarms.")
    L.append("")

    L.append("## 3. Probability-shift analysis")
    L.append("")
    L.append("### Distribution stats (oil probability)")
    L.append("")
    L.append("| Class | Model | Mean | Median | p10 | p90 |")
    L.append("|---|---:|---:|---:|---:|---:|")
    L.append(f"| Non-Oil | Baseline | {base_non['mean']} | {base_non['median']} | {base_non['p10']} | {base_non['p90']} |")
    L.append(f"| Non-Oil | Robust | {rob_non['mean']} | {rob_non['median']} | {rob_non['p10']} | {rob_non['p90']} |")
    L.append(f"| Oil | Baseline | {base_oil['mean']} | {base_oil['median']} | {base_oil['p10']} | {base_oil['p90']} |")
    L.append(f"| Oil | Robust | {rob_oil['mean']} | {rob_oil['median']} | {rob_oil['p10']} | {rob_oil['p90']} |")
    L.append("")

    def fmt_head(df_h, label):
        L.append(f"### {label}")
        L.append("")
        L.append("| image_path (base name) | true | base_p | rob_p | delta |")
        L.append("|---|---:|---:|---:|---:|")
        for _, r in df_h.iterrows():
            import os
            L.append(f"| `{os.path.basename(str(r['image_path']))}` | {int(r['true_label'])} | {r['baseline_prob']:.4f} | {r['robust_prob']:.4f} | {r['prob_delta']:+.4f} |")
        L.append("")

    fmt_head(top_up, "Top 10 largest probability increases")
    fmt_head(top_down, "Top 10 largest probability decreases")

    L.append("## 4. Highest-confidence transition cases")
    L.append("")
    for label, sdf in [("Augmentation fixed a baseline FN (highest robust prob)", fn2tp),
                       ("Augmentation created a new FN (highest baseline prob)", tp2fn),
                       ("Augmentation fixed a baseline FP (highest baseline prob)", fp2tn),
                       ("Augmentation created a new FP (highest robust prob)", tn2fp)]:
        L.append(f"### {label}")
        L.append("")
        L.append("| image_path (base name) | true | base_p | rob_p | context |")
        L.append("|---|---:|---:|---:|---:|")
        for _, r in sdf.iterrows():
            import os
            L.append(f"| `{os.path.basename(str(r['image_path']))}` | {int(r['true_label'])} | {r['baseline_prob']:.4f} | {r['robust_prob']:.4f} | {r['context_type']} |")
        L.append("")

    L.append("## 5. ROC-AUC and fixed-threshold behaviour (no threshold tuning)")
    L.append("")
    L.append(f"- Baseline ROC-AUC: **{base_auc:.4f}**")
    L.append(f"- Robustness ROC-AUC: **{robust_auc:.4f}**")
    L.append("")
    L.append("Both AUCs are computed on the identical held-out test set using the untuned probability scores. The fixed decision threshold was not changed or selected on the test set.")
    L.append("")

    L.append("## 6. Evidence-based recommendation for the next experiment")
    L.append("")
    L.append("(Recommendation will be summarized from the diagnostic tables above.)")
    L.append("")

    report = "\n".join(L)
    (OUTPUT_DIR / "COMPARATIVE_ANALYSIS.md").write_text(report, encoding="utf-8")

    # ---- Console summary ----
    print("=== CONSISTENCY CHECK ===")
    print(f"baseline pred sum: {int(df_out['baseline_pred'].sum())}, robust pred sum: {int(df_out['robust_pred'].sum())}")
    print(f"Baseline AUC: {base_auc:.4f}, Robust AUC: {robust_auc:.4f}")
    print(f"Baseline TP/TN/FP/FN: {base_cm['TP']}/{base_cm['TN']}/{base_cm['FP']}/{base_cm['FN']}")
    print(f"Robust TP/TN/FP/FN: {robust_cm['TP']}/{robust_cm['TN']}/{robust_cm['FP']}/{robust_cm['FN']}")
    print("Transition groups:")
    print(tg.to_string())
    print("Wrote comparative_predictions.csv and COMPARATIVE_ANALYSIS.md")


if __name__ == "__main__":
    main()
