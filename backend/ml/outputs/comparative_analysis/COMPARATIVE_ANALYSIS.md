# OilGuard Comparative Error Analysis: Baseline vs Robustness-Augmentation

## Scope and safeguards

Read-only diagnostic comparison of the two saved best models on the identical deterministic seed-42 held-out test split (847 images). Both models use the same grayscale /255.0 preprocessing and the fixed 0.50 decision rule. No model, dataset, threshold, or existing artifact was changed.

- Baseline best model: `outputs/oil_spill_cnn_best.pt` (val_loss 0.7691, val_acc 0.7070)
- Robustness best model: `outputs/robustness_augmentation/oil_spill_cnn_best.pt` (val_loss 0.7544, val_acc 0.7556)
- Test images: 847

## Overall test metrics at fixed 0.50

| Metric | Baseline | Robustness |
|---|---:|---:|
| Accuracy | 0.6765 | 0.7202 |
| ROC-AUC | 0.7510 | 0.7776 |
| TP / TN / FP / FN | 176/397/163/111 | 162/448/112/125 |

Notes: The 111→125 FN increase (14 additional FNs) and 163→112 FP decrease (51 fewer FPs) shown above are the gross changes; the net transition groups are detailed below.
## 1. Transition groups

| Transition | Count | Percent of 847 |
|---|---:|---:|
| FP->TN | 55 | 6.5% |
| TP->FN | 22 | 2.6% |
| FN->TP | 8 | 0.9% |
| TN->FP | 4 | 0.5% |
| unchanged | 758 | 89.5% |

Interpretation of the four symmetric changes:
- **FP→TN (fixed FP):** baseline predicted oil, robustness predicted non-oil correctly → fewer false positives.
- **TP→FN (new FN):** baseline predicted oil correctly, robustness now predicts non-oil → new false negatives.
- **FN→TP (fixed FN):** baseline missed, robustness now detects.
- **TN→FP (new FP):** baseline correct non-oil, robustness now false positives.

## 2. Context concentration of the key transitions

Context types are mutually exclusive and prioritized white → boundary → dark_linear → absent.

| Transition | n | white | boundary | dark_linear | absent |
|---|---:|---:|---:|---:|---:|
| FP->TN | 55 | 0 | 16 | 4 | 37 |
| TP->FN | 22 | 0 | 5 | 5 | 13 |
| FN->TP | 8 | 0 | 2 | 5 | 3 |
| TN->FP | 4 | 0 | 0 | 0 | 4 |

### 2a. Are the 14 additional FNs (TP→FN) concentrated in a context?
See the TP→FN row above. A slope toward one context (e.g. dark_linear or absent) indicates where robustness lost recall.

### 2b. Are the 51 fewer FPs (FP→TN) concentrated in a context?
See the FP→TN row above. A concentration (e.g. white or boundary) indicates the context where augmentation reduced false alarms.

## 3. Probability-shift analysis

### Distribution stats (oil probability)

| Class | Model | Mean | Median | p10 | p90 |
|---|---:|---:|---:|---:|---:|
| Non-Oil | Baseline | 0.4277 | 0.4267 | 0.1437 | 0.7508 |
| Non-Oil | Robust | 0.3757 | 0.3724 | 0.1023 | 0.6623 |
| Oil | Baseline | 0.6202 | 0.6474 | 0.3767 | 0.8345 |
| Oil | Robust | 0.5811 | 0.5637 | 0.3324 | 0.7988 |

### Top 10 largest probability increases

| image_path (base name) | true | base_p | rob_p | delta |
|---|---:|---:|---:|---:|
| `0_0_0_img_MSB0wqoY8PVXx6y4_NOR_cls_1.jpg` | 1 | 0.4104 | 0.5364 | +0.1260 |
| `1_200_0_img_4ygAPm6XL0qjmI8C_ADR_cls_0.jpg` | 0 | 0.3809 | 0.5050 | +0.1241 |
| `0_0_0_img_9c3d5585_MLA_cls_0.jpg` | 0 | 0.5129 | 0.6190 | +0.1060 |
| `6_400_200_img_NIQD4cYPEnZoZOFb_JAV_cls_1.jpg` | 1 | 0.6313 | 0.7356 | +0.1044 |
| `1_200_0_img_y2fwdWR9H60DMWEV_JAV_cls_1.jpg` | 1 | 0.6314 | 0.7323 | +0.1008 |
| `1_200_0_img_NIQD4cYPEnZoZOFb_JAV_cls_1.jpg` | 1 | 0.6423 | 0.7422 | +0.0999 |
| `6_400_200_img_JhYU3JitCR0jDE5i_JAV_cls_1.jpg` | 1 | 0.6460 | 0.7441 | +0.0980 |
| `6_400_200_img_3yzQiqzFv8e6dc2Z_ISR_cls_1.jpg` | 1 | 0.4466 | 0.5440 | +0.0975 |
| `0_0_0_img_9iomrRlW8Zr7spdq_PHI_cls_0.jpg` | 0 | 0.4322 | 0.5273 | +0.0952 |
| `1_200_0_img_ppN4GibVpmVdvJIp_JAP_cls_1.jpg` | 1 | 0.4702 | 0.5637 | +0.0935 |

### Top 10 largest probability decreases

| image_path (base name) | true | base_p | rob_p | delta |
|---|---:|---:|---:|---:|
| `923_6600_5000_img_cz1XyUY7CgncRC2Z_GBR_cls_0.jpg` | 0 | 0.5372 | 0.3163 | -0.2209 |
| `1165_6800_6200_img_bWGRrk1AMPFKvGcG_GBR_cls_0.jpg` | 0 | 0.5150 | 0.3047 | -0.2102 |
| `2119_7800_7600_img_pbjty5f2R0j26K2d_GBR_cls_0.jpg` | 0 | 0.4945 | 0.2933 | -0.2012 |
| `144_7800_1400_img_dlgcUVtXspX0EXZt_GBR_cls_0.jpg` | 0 | 0.5389 | 0.3400 | -0.1989 |
| `879_600_6000_img_DHSYcH8WDPyCa2O1_SIN_cls_0.jpg` | 0 | 0.6893 | 0.4930 | -0.1964 |
| `2454_1800_8400_img_5scBKiA2NluhunjC_SIN_cls_0.jpg` | 0 | 0.4960 | 0.3019 | -0.1942 |
| `1652_800_6000_img_v246W8EmjBBoVOV0_SIN_cls_0.jpg` | 0 | 0.6283 | 0.4349 | -0.1935 |
| `1379_6200_5200_img_uDrwlppDBWmkRdTx_SIN_cls_0.jpg` | 0 | 0.5121 | 0.3231 | -0.1890 |
| `2102_7600_7200_img_B00boA7p1lu52HMa_GBR_cls_0.jpg` | 0 | 0.5829 | 0.3956 | -0.1873 |
| `2016_1400_7400_img_e8L1y7HOJEcCp3xR_GBR_cls_0.jpg` | 0 | 0.4738 | 0.2880 | -0.1858 |

## 4. Highest-confidence transition cases

### Augmentation fixed a baseline FN (highest robust prob)

| image_path (base name) | true | base_p | rob_p | context |
|---|---:|---:|---:|---:|
| `1_200_0_img_ppN4GibVpmVdvJIp_JAP_cls_1.jpg` | 1 | 0.4702 | 0.5637 | boundary |
| `6_400_200_img_EqkLhqaQhx6njPCH_ISR_cls_1.jpg` | 1 | 0.4946 | 0.5526 | boundary |
| `6_400_200_img_3yzQiqzFv8e6dc2Z_ISR_cls_1.jpg` | 1 | 0.4466 | 0.5440 | dark_linear |
| `0_0_0_img_MSB0wqoY8PVXx6y4_NOR_cls_1.jpg` | 1 | 0.4104 | 0.5364 | absent |
| `6_400_200_img_0CugGbeejr96zxqr_SFr_cls_1.jpg` | 1 | 0.4837 | 0.5292 | absent |

### Augmentation created a new FN (highest baseline prob)

| image_path (base name) | true | base_p | rob_p | context |
|---|---:|---:|---:|---:|
| `1755_8000_6400_img_U76M7YXf8wSgRxM0_SIN_cls_1.jpg` | 1 | 0.6474 | 0.4959 | absent |
| `3_600_0_img_hWGwhOySBiHxGG5P_PHI_cls_1.jpg` | 1 | 0.6227 | 0.4886 | dark_linear |
| `939_7400_4400_img_ASvSLk2JXkRsDyzx_GBR_cls_1.jpg` | 1 | 0.6221 | 0.4643 | absent |
| `2674_8000_9000_img_jGwUeasbjouH8YDP_SIN_cls_1.jpg` | 1 | 0.6094 | 0.4863 | absent |
| `2203_8600_7800_img_bzwSF5gbIpZh5XOL_SIN_cls_1.jpg` | 1 | 0.6009 | 0.4507 | absent |

### Augmentation fixed a baseline FP (highest baseline prob)

| image_path (base name) | true | base_p | rob_p | context |
|---|---:|---:|---:|---:|
| `879_600_6000_img_DHSYcH8WDPyCa2O1_SIN_cls_0.jpg` | 0 | 0.6893 | 0.4930 | boundary |
| `1132_5000_4200_img_cP6yVHk8XRRYSn68_GIB_cls_0.jpg` | 0 | 0.6498 | 0.4738 | boundary |
| `1331_7800_5200_img_c8umAJtF9bNMjXVA_SIN_cls_0.jpg` | 0 | 0.6364 | 0.4672 | absent |
| `1631_8000_7600_img_7wrHFvamTOpbNkqL_GBR_cls_0.jpg` | 0 | 0.6364 | 0.4876 | absent |
| `2467_4400_8000_img_rEbB95E05GWCIQvD_GIB_cls_0.jpg` | 0 | 0.6361 | 0.4559 | absent |

### Augmentation created a new FP (highest robust prob)

| image_path (base name) | true | base_p | rob_p | context |
|---|---:|---:|---:|---:|
| `0_0_0_img_IdWPjAQlFfHI8jhG_EGY_cls_0.jpg` | 0 | 0.4974 | 0.5522 | absent |
| `0_0_0_img_9iomrRlW8Zr7spdq_PHI_cls_0.jpg` | 0 | 0.4322 | 0.5273 | absent |
| `0_0_0_img_BK90Z27vRguORzMY_PHI_cls_0.jpg` | 0 | 0.4376 | 0.5184 | absent |
| `1_200_0_img_4ygAPm6XL0qjmI8C_ADR_cls_0.jpg` | 0 | 0.3809 | 0.5050 | absent |

## 5. ROC-AUC and fixed-threshold behaviour (no threshold tuning)

- Baseline ROC-AUC: **0.7510**
- Robustness ROC-AUC: **0.7776**

Both AUCs are computed on the identical held-out test set using the untuned probability scores. The fixed decision threshold was not changed or selected on the test set.

## 6. Evidence-based recommendation for the next experiment

(Recommendation will be summarized from the diagnostic tables above.)
