# Final Test Evaluation: Experiment 2 (Class Weight 2.5 + Robustness Augmentation)

## Scope

ONE-TIME evaluation on the untouched 847-image test set using frozen candidate deployment threshold 0.52.
Read-only: no retraining, no model changes, no dataset changes.

## Results

| Model | Threshold | Accuracy | Precision | Recall | Oil F1 | ROC-AUC | TP | TN | FP | FN |
|-------|-----------|----------|-----------|--------|--------|---------|----|----|----|----|
| Baseline | 0.50 | 0.6765 | 0.5192 | 0.6132 | 0.5623 | 0.7510 | 176 | 397 | 163 | 111 |
| Experiment2 | 0.50 | 0.6458 | 0.4871 | 0.8537 | 0.6203 | 0.7623 | 245 | 302 | 258 | 42 |
| Experiment2 | 0.52 | 0.6694 | 0.5074 | 0.8362 | 0.6316 | 0.7623 | 240 | 327 | 233 | 47 |

## Confusion Matrices

### Baseline at 0.50

| | Pred Non-Oil | Pred Oil |
|---|---:|---:|
| Actual Non-Oil | 397 | 163 |
| Actual Oil | 111 | 176 |

### Experiment2 at 0.50

| | Pred Non-Oil | Pred Oil |
|---|---:|---:|
| Actual Non-Oil | 302 | 258 |
| Actual Oil | 42 | 245 |

### Experiment2 at 0.52

| | Pred Non-Oil | Pred Oil |
|---|---:|---:|
| Actual Non-Oil | 327 | 233 |
| Actual Oil | 47 | 240 |
