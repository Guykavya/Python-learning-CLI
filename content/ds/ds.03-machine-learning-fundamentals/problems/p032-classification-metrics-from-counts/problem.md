# Classification metrics from counts

Chapter section 12. From the four counts of a confusion matrix you can compute every classification metric:

```text
accuracy    = (TP + TN) / (TP + FP + FN + TN)
precision   = TP / (TP + FP)        "of the cases I flagged, how many were real?"
recall      = TP / (TP + FN)        "of the real cases, how many did I find?"
specificity = TN / (TN + FP)
F1          = 2 * precision * recall / (precision + recall)
```

Some of these divide by zero (for example, a model that never says "positive" has `TP + FP = 0`). Here the convention is: **a metric whose denominator is 0 is 0.0**, with **no warning and no exception**.

Write `cls_metrics(TP, FP, FN, TN)` returning a dict with the keys `accuracy`, `precision`, `recall`, `specificity`, `f1` (plain floats). Negative counts raise `ValueError`.

## Example

```text
cls_metrics(TP=8, FP=2, FN=4, TN=86)  ->  {"accuracy": 0.94, "precision": 0.8, "recall": 0.666..., "specificity": 0.977..., "f1": 0.727...}
cls_metrics(TP=0, FP=0, FN=20, TN=980) -> accuracy 0.98 but precision 0.0, recall 0.0, f1 0.0
```
