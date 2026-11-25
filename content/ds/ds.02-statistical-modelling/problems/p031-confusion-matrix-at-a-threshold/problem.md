# Confusion matrix at a threshold

Chapter section 13.8. A logistic model gives probabilities. To make a yes/no decision you pick a **threshold**: predict positive when `p >= threshold`. Count what happens:

| | predicted positive | predicted negative |
|---|---|---|
| actually positive (y = 1) | TP | FN |
| actually negative (y = 0) | FP | TN |

Write `confusion_at(y, p, threshold)` returning a dict with the four **integer** counts `{"TP": ..., "FP": ..., "FN": ..., "TN": ...}`. A row is predicted positive when `p >= threshold` (equal counts as positive).

## Example

```text
y = [1, 0, 1, 0, 1, 0]      p = [0.9, 0.8, 0.6, 0.4, 0.3, 0.1]
confusion_at(y, p, 0.5)  ->  {"TP": 2, "FP": 1, "FN": 1, "TN": 2}
confusion_at(y, p, 0.0)  ->  {"TP": 3, "FP": 3, "FN": 0, "TN": 0}     # everyone positive
confusion_at(y, p, 1.0)  ->  {"TP": 0, "FP": 0, "FN": 3, "TN": 3}     # nobody positive
```
