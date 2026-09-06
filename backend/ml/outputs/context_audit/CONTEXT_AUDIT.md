# OilGuard Data / Context Audit

## Scope and safeguards

- **Images analyzed:** all 5,630 CSIRO patches using the deterministic 70/15/15 split recreated through `prepare_data()` with its fixed seed (42).
- **Split sizes:** train 3,940; validation 843; test 847.
- **Prediction join:** the existing 847-row `test_predictions.csv` at the existing 0.50 decision rule; no prediction was regenerated and no threshold was changed.
- **No training, architecture, model, dataset, configuration, threshold, or existing-file changes** were made.

## Important interpretation constraint

A single 400×400 grayscale patch cannot prove that an observed feature is coastline, land, a vessel, oil, an acquisition artifact, or no-data without geospatial/source metadata and expert review. The three contexts below are **auditable image-based candidates**, not semantic ground truth. Raw measurements and flags for every image are in [`context_audit_all_images.csv`](context_audit_all_images.csv).

## Candidate definitions

1. **Substantial white-region candidate:** at least 2% of pixels have intensity ≥ 250. The CSV also records the largest white component's size, border share, and bounding-box fill.
2. **Coast/land-water boundary candidate:** a long high-gradient Sobel edge component after Gaussian smoothing (at least 35% of the image side in pixels) with at least 12% of edge pixels within a 12-pixel image border. This identifies strong boundary/scene-edge candidates, not confirmed coastlines.
3. **Dark linear/curvilinear candidate:** pixels ≤ 35 form a component of at least 120 pixels with elongation ≥ 3.0 and dark-pixel coverage ≥ 0.3%. This identifies elongated dark structures, not confirmed oil, wakes, or land features.

## Prevalence by class

| Context | Overall n / % | Non-Oil n / % | Oil n / % | Oil − Non-Oil (pp) |
|---|---:|---:|---:|---:|
| Substantial white-region candidate | 1217 / 21.62% | 1127 / 30.26% | 90 / 4.72% | -25.53 |
| Coast/land-water boundary candidate | 989 / 17.57% | 758 / 20.35% | 231 / 12.13% | -8.22 |
| Dark linear/curvilinear candidate | 869 / 15.44% | 479 / 12.86% | 390 / 20.47% | +7.61 |

## Split distribution screen

A difference of **5 percentage points or more** between the largest and smallest split prevalence is treated as material for this descriptive screen.

### Substantial white-region candidate

| Split | Flagged / total | Percentage |
|---|---:|---:|
| Train | 869 / 3940 | 22.06% |
| Validation | 177 / 843 | 21.00% |
| Test | 171 / 847 | 20.19% |

No material absolute spread under the predeclared 5-point screen (range: 1.87 points).
### Coast/land-water boundary candidate

| Split | Flagged / total | Percentage |
|---|---:|---:|
| Train | 688 / 3940 | 17.46% |
| Validation | 150 / 843 | 17.79% |
| Test | 151 / 847 | 17.83% |

No material absolute spread under the predeclared 5-point screen (range: 0.37 points).
### Dark linear/curvilinear candidate

| Split | Flagged / total | Percentage |
|---|---:|---:|
| Train | 619 / 3940 | 15.71% |
| Validation | 140 / 843 | 16.61% |
| Test | 110 / 847 | 12.99% |

No material absolute spread under the predeclared 5-point screen (range: 3.62 points).

## Test-set error rates at the existing 0.50 rule

FP rate is FP divided by the number of actual non-oil images in that context subset. FN rate is FN divided by actual oil images in that context subset. Precision and recall are calculated within the stated subset; small subsets should be interpreted cautiously.

### Substantial white-region candidate

| Test subset | Images | Non-Oil | Oil | FP / FP rate among non-oil | FN / FN rate among oil | Precision | Recall |
|---|---:|---:|---:|---:|---:|---:|---:|
| Candidate present | 171 | 158 | 13 | 0 / 0.00% | 13 / 100.00% | N/A | 0.0000 |
| Candidate absent | 676 | 402 | 274 | 163 / 40.55% | 98 / 35.77% | 0.5192 | 0.6423 |
### Coast/land-water boundary candidate

| Test subset | Images | Non-Oil | Oil | FP / FP rate among non-oil | FN / FN rate among oil | Precision | Recall |
|---|---:|---:|---:|---:|---:|---:|---:|
| Candidate present | 151 | 109 | 42 | 23 / 21.10% | 32 / 76.19% | 0.3030 | 0.2381 |
| Candidate absent | 696 | 451 | 245 | 140 / 31.04% | 79 / 32.24% | 0.5425 | 0.6776 |
### Dark linear/curvilinear candidate

| Test subset | Images | Non-Oil | Oil | FP / FP rate among non-oil | FN / FN rate among oil | Precision | Recall |
|---|---:|---:|---:|---:|---:|---:|---:|
| Candidate present | 110 | 64 | 46 | 4 / 6.25% | 35 / 76.09% | 0.7333 | 0.2391 |
| Candidate absent | 737 | 496 | 241 | 159 / 32.06% | 76 / 31.54% | 0.5093 | 0.6846 |

## Are bright white regions likely masking/artifact patterns?

There are **1217** substantial white-region candidates. Among them:

- **1171 (96.2%)** have a largest near-white component of at least 1,000 pixels (0.625% of a 400×400 patch).
- **38 (3.1%)** have that largest near-white component touching an image border.
- **825 (67.8%)** have a largest near-white component filling at least half of its bounding box.

The measurements provide **suggestive but not conclusive** evidence of non-scene/image-processing effects: very large, filled near-white components are common, and the earlier high-confidence FN contact sheet contains several sharply bounded, block-like white regions. However, only 3.1% of the largest components touch the patch edge, so this audit does **not** support claiming that most flagged regions are scene-edge or no-data masks. Near-white SAR pixels can also be valid high-backscatter or clipped/saturated returns. The defensible conclusion is that these are a high-priority **artifact-like candidate subset** requiring source-scene metadata and manual review before any masking, filtering, or preprocessing rule is adopted.

## Assessment and next experiment

The audit should guide action only where its measured class/split prevalence and context-conditioned error rates show a repeatable association. If a candidate is disproportionately class- or split-concentrated and has a clearly worse test error rate, it supports a **targeted manual label/context review** of that candidate subset first. Do not apply mask-aware preprocessing, augmentation, or rebalancing merely from these proxy flags.

**Recommended next experiment:** draw a stratified, read-only manual review sample across the three image-based candidate flags and their unflagged controls (separately by oil/non-oil and by split), with access to source-scene metadata where available. Confirm whether white areas are no-data/processing artifacts, whether boundary candidates are actual coast/land-water transitions, and whether dark structures are oil morphology or look-alikes. Use that review to decide between targeted label correction, exclusion/mask-aware preprocessing, or context-balanced augmentation; only then design a controlled retraining experiment.
