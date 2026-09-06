# OilGuard Manual / Source-Scene Context Review

## Scope and safeguards

This is a **read-only qualitative review** of a deterministic, stratified sample selected from `../context_audit/context_audit_all_images.csv`. It did not alter images, labels, model files, data splits, thresholds, configuration, or training state. It did not run inference or use test data for training or model-development decisions.

The review examined the original 400×400 raster patches and the audit's measured context fields. The local project contains no per-image acquisition metadata, geolocation, timestamp, sensor-product record, annotation provenance, or source-scene lookup table for the CSIRO patches. The local filename convention is documented only as:

```text
[x]_[y]_[z]_img_[unique_id]_[country]_cls_[label].jpg
```

The trailing three-letter token is a country/region code in the project documentation (for example `GBR`, `SIN`, `JAV`, `PHI`, `EGY`); it is **not** sufficient to establish precise location, acquisition conditions, vessel presence, coastline, or oil morphology. Consequently, all semantic calls below are patch-level interpretations, not confirmations.

## Selection design

The review contains **36 unique patches**:

- **13/13** oil-labelled test patches with a substantial white-region candidate, all of which were already false negatives at the fixed 0.50 reporting rule. These were prioritized as requested and are described individually below.
- A median-by-candidate-metric patch for every feasible combination of each candidate flag × class × split: 18 intended strata, with two overlapping priority selections reducing the number of additional unique images.
- One context-absent control for every class × split cell: 6 controls.

An image may appear in more than one candidate group; that is an intended property of the audit flags rather than a sampling error. “Context absent” means all three audit flags are false; it does not mean the patch contains no visual structure.

## How to read the findings

### Measured evidence

The audit fields are objective image-derived measurements:

- **White candidate:** at least 2% of pixels at intensity ≥250.
- **Boundary candidate:** a qualifying long high-gradient Sobel component with the audit's border-related criteria.
- **Dark-linear candidate:** a qualifying dark connected component (pixels ≤35) with the audit's size, coverage, and elongation criteria.

### Interpretation labels

The requested labels are applied conservatively:

- **Likely processing/no-data artifact** means a sharp, blocky, saturated, non-natural-looking region or cutout is visible. It remains *likely*, not confirmed, without source data.
- **Likely saturation/clipping** means a visibly near-uniform pure-white region with abrupt geometric edges is present.
- **Plausible valid SAR backscatter** means texture is continuous and scene-like, without a clear patch-boundary/fill signature.
- **Plausible coastline/land-water boundary**, **vessel/wake**, **oil-like morphology**, and **sea-state/wind/current pattern** are visual hypotheses only.
- **Ambiguous/uncertain** is used wherever a 400×400 grayscale patch cannot distinguish plausible alternatives.

None of these visual calls changes the dataset label or implies the labelled oil/non-oil category is wrong.

## Prioritized review: all 13 white-candidate oil test images

All 13 are oil-labelled test images, all were false negatives at the already-existing 0.50 reporting rule, and all have the white candidate flag. Their observed error status is reported only for diagnosis; it must not be used to tune a model or threshold.

| File (truncated) | Measured white fraction | Visual observation | Conservative interpretation | Confidence / limitation |
|---|---:|---|---|---|
| `100_5800_800..._SIN_cls_1.jpg` | 24.23% | Large bright region with a sharp stair-stepped boundary; dark elongated feature crosses otherwise textured area. | Likely clipping/no-data or processing fill **plus** ambiguous dark linear feature. Not enough evidence to call the dark feature oil or a wake. | Moderate for bright-region artifact-like appearance; low for dark-feature semantics. |
| `1195_11000_5200..._GBR_cls_1.jpg` | 6.07% | Patch is dominated by an abrupt dark-to-light transition and a narrow dark boundary. | Plausible land/water or scene boundary; white flag may be high-backscatter/bright scene texture rather than a mask. | Low–moderate; no geolocation/source scene. |
| `1488_5600_6600..._GBR_cls_1.jpg` | 27.33% | Thin, branching dark curvilinear structure on bright textured background. | Ambiguous dark linear structure; plausible oil-like morphology, wake/current line, or another look-alike. White flag does not visibly present as a large fill. | Low semantic confidence. |
| `1714_4800_7200..._GBR_cls_1.jpg` | 3.69% | Thick dark curving boundary crosses the patch. | Plausible land/water boundary or complex dark linear/curvilinear scene feature; not identifiable as oil. | Low–moderate. |
| `1889_8600_6600..._SIN_cls_1.jpg` | 5.50% | Bright-white angular/stepped areas on both sides of a darker scene with a central dark object. | Strongest artifact-like sample: likely saturated/clipped or processing/no-data regions. Central dark object is ambiguous; could be a dark target/feature, not confirmable as oil or vessel. | Moderate for saturation/clipping appearance; low otherwise. |
| `232_4800_1600..._SIN_cls_1.jpg` | 2.77% | Dark left-side region with sharp transition, small dark targets, and a white edge wedge. | Plausible scene boundary combined with an artifact-like bright edge; vessel/wake cannot be confirmed. | Low–moderate. |
| `2793_11000_9600..._GBR_cls_1.jpg` | 5.84% | Oblique bright-white cutout at top and narrow dark line beneath it. | Likely clipping/no-data or processing artifact; dark line is ambiguous. | Moderate for artifact-like bright area. |
| `312_5800_2000..._GBR_cls_1.jpg` | 7.36% | Several dark linear features, including a broad dark band, on a bright textured scene. | Ambiguous dark lineation; plausible oil-like morphology, wake/current pattern, or boundary. No basis to choose one. | Low semantic confidence. |
| `357_5800_2200..._GBR_cls_1.jpg` | 7.36% | Bright vertical blank region with several very bright points and a dark band on the textured side. | Likely clipping/no-data/process fill at right; bright points are compatible with high-backscatter targets but do not prove vessels. | Moderate for artifact-like region; low for target identity. |
| `496_14800_2000..._GBR_cls_1.jpg` | 3.63% | Mostly homogeneous textured area with a small bright edge wedge and no distinct oil feature. | Plausible valid SAR backscatter with a limited artifact-like boundary; oil morphology not visually resolvable. | Low. |
| `4_0_200..._EGY_cls_1.jpg` | 13.18% | Multiple extremely bright point/linear returns on a structured background and a dark tapered region. | Bright returns are compatible with man-made/high-backscatter targets; dark region could be oil-like, wake-related, or another look-alike. A vessel/wake is plausible but unconfirmed. | Low–moderate. |
| `575_15200_2200..._GBR_cls_1.jpg` | 51.21% | Large sharply bounded stepped white region with dark elongated objects nearby. | Very strong clipping/no-data/process-artifact candidate. The dark objects could be targets, wakes, or oil-like features; cannot be disambiguated. | High for saturated/clipped appearance; low for object semantics. |
| `577_10800_2600..._SIN_cls_1.jpg` | 4.44% | Small blocky bright region adjacent to multiple dark compact/elongated features. | Likely small artifact-like bright fill; dark features are ambiguous and possibly target/wake-like, but not verified. | Moderate for bright fill; low for dark features. |

### What the priority set supports—and does not support

**Measured:** white coverage ranges from **2.77% to 51.21%** in these 13 images; all satisfy the predeclared white-pixel criterion and all were false negatives in the fixed historical test prediction file.

**Interpretation:** 6–7 of the 13 visually show sharply geometric or stepped pure-white regions consistent with a clipping/no-data/processing-artifact hypothesis. The remainder show bright or high-backscatter areas without a decisive mask-like geometry. The set therefore supports treating white candidates as a heterogeneous review cohort—not as confirmed masks and not as a universal filtering target.

## Stratified candidate and control review

This table covers the non-priority representative selections. The feature call describes the visually most salient candidate-related evidence, not all content in the patch.

| Context / split / class | File (truncated) | Measured evidence | Patch-level interpretation | Confidence / limitation |
|---|---|---|---|---|
| White / train / non-oil | `771_13200_8200...GBR...0` | White 17.87%; also dark flag | Mostly continuous textured return with a dark corner feature; no obvious uniform white fill. | Plausible valid SAR backscatter; dark feature ambiguous. Low. |
| White / train / oil | `413_3000_2200...SIN...1` | White 10.39% | Broad near-white field with a hard dark right edge. | Ambiguous; could be contrast/saturation transition or land/water boundary. Low–moderate. |
| White / validation / non-oil | `1045_7000_5600...GBR...0` | White 22.18% | Large bright area and sharply bounded dark region, with a stepped white bottom edge. | Likely processing/no-data/clipping component; boundary itself cannot be assigned. Moderate. |
| White / validation / oil | `725_11800_5000...SIN...1` | White 6.48% | Bright textured patch with a thick dark curved band and a point target. | Plausible dark linear/curvilinear scene feature; point may be a high-backscatter target, not confirmed vessel. Low. |
| White / test / non-oil | `2276_1000_7800...GBR...0` | White 20.81% | Broad homogeneous gray texture interrupted by a sharp stepped bright region. | Likely processing/no-data/clipping candidate; no oil-like call. Moderate. |
| Boundary / train / non-oil | `2388_12400_8800...SIN...0` | Boundary; white 89.16%; dark flag | Very large uniform white region with a narrow dark edge. | Strong clipping/no-data/process-fill candidate rather than confirmed coastline. High visual confidence for fill-like appearance; no source confirmation. |
| Boundary / train / oil | `2199_7600_7800...SIN...1` | Boundary; dark flag | Bright scene with a narrow dark curvilinear boundary. | Plausible coastline/land-water or linear scene feature; oil morphology cannot be confirmed. Low. |
| Boundary / validation / non-oil | `2351_5400_9800...GBR...0` | Boundary | Curved dark boundary at a white patch edge. | Likely edge/clipping artifact with adjacent dark scene; coastline remains unverified. Moderate. |
| Boundary / validation / oil | `3_600_0...PHI...1` | Boundary | Long, branching dark curvilinear feature on textured background. | Ambiguous: plausible oil-like morphology, wake/current line, or land/water feature. Low. |
| Boundary / test / non-oil | `1871_8400_8200...GBR...0` | Boundary; white 6.49% | Dark, fairly homogeneous scene with a bright border wedge. | Likely patch-edge/clipping effect; not confirmed coast/land. Moderate. |
| Boundary / test / oil | `8_0_400...JAV...1` | Boundary; extreme dark elongation | Long narrow dark line across an otherwise smooth gray field. | Plausible oil-like morphology or wake/current line; insufficient evidence to distinguish. Low. |
| Dark / train / non-oil | `145_2600_1400...GBR...0` | Dark elongation 6.28 | Subtle elongated dark gradient/line next to a bright edge form. | Ambiguous; likely scene texture/contrast structure rather than identifiable oil. Low. |
| Dark / train / oil | `5_200_200...PHI...1` | Dark elongation 5.30 | Curvilinear dark band traverses mostly uniform background. | Plausible oil-like morphology or wake/current pattern; cannot adjudicate. Low. |
| Dark / validation / non-oil | `0_0_0...LUC...0` | Dark elongation 6.49; white 77.70% | Strong white cutout beside a dark textured strip. | Likely clipping/no-data/process fill; dark linear measure likely reflects the adjacent edge. Moderate–high for artifact-like region. |
| Dark / validation / oil | `219_11800_3600...GBR...1` | Dark elongation 5.86 | Compact, tapered dark object with trailing extension. | Could be oil-like morphology or a target/wake-like feature; uncertain. Low. |
| Dark / test / non-oil | `1467_9200_7200...GBR...0` | Dark elongation 5.63 | Smooth dark scene with a subtle diagonal line. | Ambiguous sea-state/wind/current or processing/texture line; no vessel/oil evidence. Low. |
| Dark / test / oil | `4_0_200...ADR...1` | Dark elongation 7.04 | Long irregular dark line across a smooth field. | Plausible oil-like morphology or wake/current pattern; cannot distinguish. Low. |
| Absent control / train / non-oil | `1888_6800_6600...SIN...0` | All flags absent | Low-contrast texture with a small bright point and faint linear trace. | Plausible valid SAR backscatter/sea-state texture; no decisive candidate feature. Low. |
| Absent control / train / oil | `2_400_0...GBR...1` | All flags absent | Long dark meandering band on uniform gray background. | Visually oil-like by morphology, but label semantics cannot be verified; also plausible natural/current pattern. Low. |
| Absent control / validation / non-oil | `1_200_0...GBR...0` | All flags absent | Curved dark line and mottled texture. | Plausible sea-state/current texture look-alike; uncertain. Low. |
| Absent control / validation / oil | `360_11600_2400...GBR...1` | All flags absent | Curved/branching dark lineation on bright textured field. | Plausible oil-like morphology or wake/current pattern; uncertain. Low. |
| Absent control / test / non-oil | `1_200_0...GBR...0` | All flags absent; historical FP | Thin dark line on textured background. | Plausible sea-state/current or other look-alike. Does not display a clear vessel or verified oil signature. Low. |
| Absent control / test / oil | `2_400_0...PHI...1` | All flags absent; historical TP | Broad, nearly homogeneous gray texture. | Plausible valid SAR backscatter with no visually distinctive morphology at patch scale. Low. |

## Cross-cutting findings

### 1. White candidate is a real visual heterogeneity signal, not a confirmed artifact label

The prioritized test subset includes multiple stepped, saturated, geometrically bounded white regions. This is meaningful corroboration of the original audit's concern that *some* white candidates may be clipping/no-data/processing effects. However, several white-flagged patches look more like continuous bright or high-backscatter textures. The evidence **does not** justify removing, masking, relabelling, or preprocessing the full white-flagged population.

### 2. Boundary and dark-linear flags capture mixed phenomena

The review confirms that both flags regularly select pronounced dark curves, long narrow lines, and strong transitions. In this patch-only review, the same visual form can reasonably represent oil-like morphology, a wake/current pattern, a shoreline/land-water transition, or a processing/scene edge. The audit correctly detects visually meaningful complexity, but it does not identify its physical cause.

### 3. Vessel/wake evidence is suggestive in isolated patches, never decisive

Some examples include bright point-like targets near elongated dark patterns (`4_0_200...EGY`, `357_5800...GBR`, `725_11800...SIN`). This is compatible with a vessel/wake hypothesis, but point-like SAR returns do not establish vessel identity, motion, or relationship to the dark structure. No vessel-based rule is justified.

### 4. Oil label and visual appearance cannot be reconciled without provenance

Several oil-labelled examples have clear dark lines or shapes, while other oil-labelled patches look nearly homogeneous. Conversely, non-oil controls can include comparable dark curves. This does not demonstrate label noise; it demonstrates that the 400×400 grayscale visual appearance alone cannot link a patch to annotation criteria, acquisition date, polarization, wind state, source-scene extent, or ancillary observations.

## Recommended next experiment

**Do not retrain or apply preprocessing yet.** The next justified step is a bounded **source-provenance review**, still read-only:

1. Obtain the original CSIRO dataset manifest or source-scene records for the reviewed patches—at minimum: Sentinel-1 scene/product identifier, acquisition time, geolocation/footprint, polarization/processing lineage, and annotation-source reference.
2. Use that information to re-review the 13 prioritized white-candidate oil test patches and a fixed stratified sample of white/boundary/dark candidates plus controls. Explicitly tag each item as: confirmed no-data/processing artifact, valid scene content, coastline/land-water, vessel/wake-supported, oil-annotation-supported, or unresolved.
3. Have a qualified SAR/oil-spill reviewer adjudicate a small protocol-defined subset before changing labels or excluding data.
4. Pre-register any downstream training experiment **using train/validation data only**. Keep the current held-out test set untouched until one fixed evaluation is run after the experiment is finalized.

### Decision gates before any future model experiment

- **Mask-aware preprocessing/exclusion:** only if source records confirm a reproducible artifact class and it is not label-dependent.
- **Targeted augmentation or context-balanced sampling:** only if confirmed scene contexts—not proxy flags alone—are underrepresented or disproportionately error-prone in train/validation data.
- **Label review/correction:** only if annotation provenance or expert review finds a specific, documented issue.
- **Architecture work:** only after the preceding data/provenance review determines that visually complex but valid SAR contexts are the principal failure mode.

No such downstream change is recommended from this report alone.
