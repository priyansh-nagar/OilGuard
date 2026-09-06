# OilGuard Baseline Error Analysis

## Scope

- **Model:** `oil_spill_cnn_best.pt` (saved best baseline model; stored validation loss `0.7691`, validation accuracy `0.7070`)
- **Evaluation:** deterministic held-out test split reproduced through `prepare_data()` from `train_baseline.py`
- **Test images:** 847
- **Inference device:** `cpu`
- **Decision rule for per-image CSV and default metrics:** oil when predicted probability is at least `0.50`

No training, dataset changes, model changes, configuration changes, or changes to existing model artifacts were performed.

## Default threshold (0.50)

| Metric | Value |
|---|---:|
| Accuracy | 0.6765 |
| Precision (Oil) | 0.5192 |
| Recall (Oil) | 0.6132 |
| F1 (Oil) | 0.5623 |
| ROC-AUC | 0.7510 |

| Actual / predicted | Non-Oil | Oil |
|---|---:|---:|
| Non-Oil | 397 (TN) | 163 (FP) |
| Oil | 111 (FN) | 176 (TP) |

- **True positives:** 176
- **True negatives:** 397
- **False positives:** 163
- **False negatives:** 111

## Probability behavior

| True class | Count | Mean probability | Median | 10th percentile | 90th percentile |
|---|---:|---:|---:|---:|---:|
| Non-Oil (0) | 560 | 0.4277 | 0.4267 | 0.1437 | 0.7508 |
| Oil (1) | 287 | 0.6202 | 0.6474 | 0.3767 | 0.8345 |

Among the tested thresholds, **0.40** has the highest F1 (0.5897), compared with 0.5623 at 0.50. Therefore, 0.50 is conservative for the F1 objective: lowering the threshold improves the observed precision/recall balance, but increases false positives.

ROC-AUC of 0.7510 indicates the model has useful ranking signal, but the false-positive and false-negative counts at 0.50 show that its probability distributions are not fully separated.

## Threshold comparison

| Threshold | Precision | Recall | F1 | TN | FP | FN | TP |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.20 | 0.3732 | 0.9895 | 0.5420 | 83 | 477 | 3 | 284 |
| 0.30 | 0.3991 | 0.9582 | 0.5635 | 146 | 414 | 12 | 275 |
| 0.40 | 0.4431 | 0.8815 | 0.5897 | 242 | 318 | 34 | 253 |
| 0.50 | 0.5192 | 0.6132 | 0.5623 | 397 | 163 | 111 | 176 |
| 0.60 | 0.5902 | 0.5470 | 0.5678 | 451 | 109 | 130 | 157 |
| 0.70 | 0.6368 | 0.4460 | 0.5246 | 487 | 73 | 159 | 128 |
| 0.80 | 0.6829 | 0.2927 | 0.4098 | 521 | 39 | 203 | 84 |

**Threshold note:** These are descriptive metrics on the held-out test set, not a recommended deployment-selection procedure. Choose any operational threshold on a validation set based on the actual cost of missed spills versus unnecessary inspections, then report the test set once at that fixed threshold.

## Most confident false positives

These are non-oil images predicted as oil with the highest confidence.

| Rank | Image path | True label | Predicted probability |
|---:|---|---:|---:|
| 1 | `C:\Users\amit nagar\Projects\oilguard\data\CSIRO\S1SAR_UnBalanced_400by400_Class_0\0\0_0_0_img_3OIdKia8rcNnaSIX_GGu_cls_0.jpg` | 0 | 0.849956 |
| 2 | `C:\Users\amit nagar\Projects\oilguard\data\CSIRO\S1SAR_UnBalanced_400by400_Class_0\0\2_400_0_img_87l9PwLlS37atgbB_JAV_cls_0.jpg` | 0 | 0.848769 |
| 3 | `C:\Users\amit nagar\Projects\oilguard\data\CSIRO\S1SAR_UnBalanced_400by400_Class_0\0\2_400_0_img_1s5xSTBuBFsYJqxV_JAV_cls_0.jpg` | 0 | 0.847556 |
| 4 | `C:\Users\amit nagar\Projects\oilguard\data\CSIRO\S1SAR_UnBalanced_400by400_Class_0\0\1_200_0_img_qnC64FKYfOU77zpF_GBR_cls_0.jpg` | 0 | 0.846266 |
| 5 | `C:\Users\amit nagar\Projects\oilguard\data\CSIRO\S1SAR_UnBalanced_400by400_Class_0\0\0_0_0_img_wC1a4tIsrusSipvY_JAV_cls_0.jpg` | 0 | 0.843410 |
| 6 | `C:\Users\amit nagar\Projects\oilguard\data\CSIRO\S1SAR_UnBalanced_400by400_Class_0\0\0_0_0_img_AQii5BYU8YeyeIEH_GBR_cls_0.jpg` | 0 | 0.837149 |
| 7 | `C:\Users\amit nagar\Projects\oilguard\data\CSIRO\S1SAR_UnBalanced_400by400_Class_0\0\2_400_0_img_uvlwTSqNnkv2fHh1_GBR_cls_0.jpg` | 0 | 0.836747 |
| 8 | `C:\Users\amit nagar\Projects\oilguard\data\CSIRO\S1SAR_UnBalanced_400by400_Class_0\0\9_200_400_img_8lVp7zn5O66AHFyV_GBR_cls_0.jpg` | 0 | 0.834987 |
| 9 | `C:\Users\amit nagar\Projects\oilguard\data\CSIRO\S1SAR_UnBalanced_400by400_Class_0\0\0_0_0_img_RVmNoa3VRQQVEc6r_GBR_cls_0.jpg` | 0 | 0.834592 |
| 10 | `C:\Users\amit nagar\Projects\oilguard\data\CSIRO\S1SAR_UnBalanced_400by400_Class_0\0\0_0_0_img_lQPkKVcgCulwJP8N_JAV_cls_0.jpg` | 0 | 0.834471 |

## Most confident false negatives

These are oil images predicted as non-oil with the lowest oil probability.

| Rank | Image path | True label | Predicted probability |
|---:|---|---:|---:|
| 1 | `C:\Users\amit nagar\Projects\oilguard\data\CSIRO\S1SAR_UnBalanced_400by400_Class_1\1\1488_5600_6600_img_remt4wSeBrESFomk_GBR_cls_1.jpg` | 1 | 0.078364 |
| 2 | `C:\Users\amit nagar\Projects\oilguard\data\CSIRO\S1SAR_UnBalanced_400by400_Class_1\1\575_15200_2200_img_vCp1JIfMABfrSU6d_GBR_cls_1.jpg` | 1 | 0.101514 |
| 3 | `C:\Users\amit nagar\Projects\oilguard\data\CSIRO\S1SAR_UnBalanced_400by400_Class_1\1\100_5800_800_img_BHCt1HYYwA5Gfia0_SIN_cls_1.jpg` | 1 | 0.148712 |
| 4 | `C:\Users\amit nagar\Projects\oilguard\data\CSIRO\S1SAR_UnBalanced_400by400_Class_1\1\2264_3200_7800_img_ROD6Kw3xdhgy2p3a_SIN_cls_1.jpg` | 1 | 0.224944 |
| 5 | `C:\Users\amit nagar\Projects\oilguard\data\CSIRO\S1SAR_UnBalanced_400by400_Class_1\1\4_0_200_img_H0HcBAzCoLADanF9_EGY_cls_1.jpg` | 1 | 0.233145 |
| 6 | `C:\Users\amit nagar\Projects\oilguard\data\CSIRO\S1SAR_UnBalanced_400by400_Class_1\1\85_8600_800_img_J5H0DemEIRe1ECm4_SIN_cls_1.jpg` | 1 | 0.241235 |
| 7 | `C:\Users\amit nagar\Projects\oilguard\data\CSIRO\S1SAR_UnBalanced_400by400_Class_1\1\82_2400_800_img_l95V6HYA7rzyc41p_SIN_cls_1.jpg` | 1 | 0.246809 |
| 8 | `C:\Users\amit nagar\Projects\oilguard\data\CSIRO\S1SAR_UnBalanced_400by400_Class_1\1\2055_1600_7200_img_y1r86gaMpV6fWzCV_SIN_cls_1.jpg` | 1 | 0.249690 |
| 9 | `C:\Users\amit nagar\Projects\oilguard\data\CSIRO\S1SAR_UnBalanced_400by400_Class_1\1\114_2400_1000_img_xZeV9BeUPMEuN8vr_SIN_cls_1.jpg` | 1 | 0.260294 |
| 10 | `C:\Users\amit nagar\Projects\oilguard\data\CSIRO\S1SAR_UnBalanced_400by400_Class_1\1\453_9400_4000_img_VHsPkqxtaM5D6LcH_GBR_cls_1.jpg` | 1 | 0.260618 |

## Recommendation

Prioritize **data/model improvements before threshold tuning**: ROC-AUC is materially higher than the default-threshold F1, while the probability distributions still overlap. A dedicated validation-set threshold should be selected only after fixing the evaluation workflow so that the held-out test set is not used for model/threshold selection. The most useful next technical experiment is to inspect the high-confidence error images for recurring SAR artifacts and add targeted augmentation or representative training examples for those patterns.

## Deliverable

The per-image inference record is in [`test_predictions.csv`](test_predictions.csv). It contains the source path, true label, predicted probability, default-threshold predicted label, and TP/TN/FP/FN classification for all 847 held-out test images.
