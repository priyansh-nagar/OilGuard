# OilGuard Visual Analysis of High-Confidence Errors

## Scope

This review inspects the contact sheet of the 10 most confident false positives (FPs) and 10 most confident false negatives (FNs) selected from the existing `test_predictions.csv`. It is a qualitative review of 400×400 grayscale SAR patches only. It does not establish ground-truth causes such as vessel identity, oil type, or acquisition conditions; those would require the source-scene metadata and expert annotation.

- **Contact sheet:** [high_confidence_errors_contact_sheet.png](high_confidence_errors_contact_sheet.png)
- **Selection:** 10 FPs with the largest oil probabilities and 10 FNs with the smallest oil probabilities.
- **Model decision threshold represented in labels:** 0.50.

No model, dataset, training configuration, threshold, or existing model artifact was changed.

## Visual findings by error class

### False positives: non-oil patches predicted as oil (probability 0.8345–0.8500)

The high-confidence FPs are visually dominated by **low-contrast, broadly homogeneous ocean texture** with fine speckle and weak, diffuse tonal variation. Most have no clearly resolved bright point target, coastline, or sharp linear boundary at contact-sheet scale.

Observed recurring patterns:

1. **Diffuse texture rather than an isolated geometric feature.** Most FPs contain subtle mottling or low-frequency tonal gradients. This suggests the baseline may associate quiet-water / weak-texture regimes with the oil class, rather than detecting a distinct, bounded slick-like structure.
2. **Weak banding or directional texture in several tiles.** A few FPs show faint diagonal/vertical texture or striping. These may be sea-state, wind/current-related texture, SAR speckle variation, or processing/acquisition effects. The contact sheet alone cannot distinguish these alternatives.
3. **One more conspicuous dark diffuse/linear region.** The FP ranked 6 (`0_0_0_img_AQii5BYU8YeyeIEH_GBR_cls_0.jpg`, p=0.8371) has a visibly darker, vertically extended diffuse feature. It is a plausible look-alike for a dark oil signature, but the non-oil label makes it a direct example of an ambiguous background pattern.
4. **No evidence of a systematic vessel signature among the selected FPs.** At this scale, the selected FPs do not consistently show the small bright point/linear-wake pattern expected for a clearly visible vessel. This does not rule out sub-resolution vessels or wakes.
5. **No obvious land/coastline contamination in the selected FPs.** Unlike the FNs, the top FPs are predominantly open-water-looking patches.

Interpretation: the top FPs are consistent with a **look-alike / sea-state texture failure mode**. The model is highly confident despite the absence of an obvious, localized oil-like boundary, which points toward limited discrimination between low-contrast ocean conditions and the oil class.

### False negatives: oil patches predicted as non-oil (probability 0.0784–0.2606)

The selected FNs are substantially more heterogeneous than the FPs. Many contain **hard boundaries, masked/no-data-looking white regions, very dark linear or curvilinear structures, and strong texture transitions**.

Observed recurring patterns:

1. **Strong white masked or no-data-looking regions / scene-edge boundaries.** At least four of the top FNs visibly include large saturated white regions with blocky or sharp edges:
   - `1488_5600_6600_img_remt4wSeBrESFomk_GBR_cls_1.jpg` (p=0.0784)
   - `575_15200_2200_img_vCp1JIfMABfrSU6d_GBR_cls_1.jpg` (p=0.1015)
   - `100_5800_800_img_BHCt1HYYwA5Gfia0_SIN_cls_1.jpg` (p=0.1487)
   - `4_0_200_img_H0HcBAzCoLADanF9_EGY_cls_1.jpg` (p=0.2331)

   These structures occupy meaningful portions of the patch and are very unlike the predominantly open-water FP set. They can dominate a small CNN using global average pooling, making an oil signature less salient.

2. **Dark curvilinear/linear features.** Several FNs contain dark, sharp, branching, or elongated features, notably the patches with probabilities 0.2412, 0.2468, 0.2497, 0.2603, and 0.2606. These could represent coast/land-water boundaries, channels, acquisition artifacts, wakes/current lines, or unusual oil morphologies. The visual evidence does not support assigning one cause with confidence.

3. **Potentially unusual oil signatures rather than smooth dark slicks.** If the class-1 annotations are correct, these images imply that some oil examples have strong boundaries, fragmented forms, or contextual clutter that differ from the simpler low-contrast open-water pattern the model appears to score as oil.

4. **Possible bright point targets in one FN.** `2055_1600_7200_img_y1r86gaMpV6fWzCV_SIN_cls_1.jpg` (p=0.2497) includes bright points adjacent to a dark feature. These may be vessel-like targets or other high-backscatter objects, but this cannot be confirmed from a single grayscale patch.

5. **Label ambiguity cannot be resolved visually.** The high-contrast or partially masked oil-labelled FNs may be valid oil scenes with difficult context, but the patch alone cannot verify whether oil is visible, whether the annotation refers to a broader scene, or whether label noise is present.

Interpretation: the dominant FN failure mode is **contextual complexity / coverage artifacts**, with potential coastline or land-water transitions and atypical oil morphology. The model’s very low probabilities on several of these cases indicate that it has learned a comparatively narrow visual proxy for the positive class.

## FP versus FN comparison

| Aspect | High-confidence FPs | High-confidence FNs |
|---|---|---|
| Overall appearance | Mostly homogeneous, low-contrast open-water texture | Heterogeneous, high-contrast patches |
| Likely visual confound | Sea-state, wind/current texture, speckle, diffuse look-alikes | White mask/no-data regions, scene edges, coast/land-water boundaries, dark linear/curvilinear structures |
| Vessels | No consistent obvious vessel pattern | One patch has bright points near a dark feature; inconclusive |
| Coast/land | Not visually prominent | Likely contributor in several tiles, but cannot be confirmed without geospatial context |
| Oil morphology implication | Model overcalls diffuse quiet-water texture as oil | Model misses cluttered, fragmented, or context-heavy oil-labelled examples |
| Preprocessing relevance | Single grayscale channel may blur subtle intensity/texture differences | Global pooling and grayscale-only input may reduce visibility of small/localized oil structures amid large masks/boundaries |

## Evidence-based next experiment

**Next experiment: perform a stratified data-quality and context audit before retraining.**

Create a read-only review set from the full train/validation/test labels that explicitly tags (or at least counts) patches with: (a) white no-data/mask coverage, (b) coastline/land-water boundaries, (c) strong dark linear features, and (d) open-water low-contrast texture. Then compare their class frequencies and baseline error rates.

Why this is the most useful next step:

- The selected FNs repeatedly contain high-contrast masks/boundaries that are largely absent from selected FPs.
- The selected FPs repeatedly show visually bland, diffuse water texture that is being assigned high oil probability.
- This separation indicates a likely **data/context shift or annotation-context issue**, not merely a decision-threshold problem.
- The audit can determine whether targeted augmentation, mask-aware cropping/filtering, context-balanced sampling, or label review is justified, without prematurely changing the CNN architecture.

Only after that audit should a future controlled experiment consider targeted preprocessing or training-data changes. Operational threshold selection should still be performed on validation data, not optimized on the held-out test set.
