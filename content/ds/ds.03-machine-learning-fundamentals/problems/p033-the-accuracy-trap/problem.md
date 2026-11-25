# The accuracy trap

Chapter section 12. In a data set of **1,000** cases, **20** are positive (for example fraud). Two models are compared by their confusion-matrix counts `(TP, FP, FN, TN)`:

```python
def metrics(tp, fp, fn, tn):
    accuracy = (tp + tn) / (tp + fp + fn + tn)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return accuracy, precision, recall, f1


models = {
    "always no": (0, 0, 20, 980),
    "alarm model": (15, 25, 5, 955),
}
for name, counts in models.items():
    a, p, r, f = metrics(*counts)
    print(f"{name}: accuracy {a:.3f}, precision {p:.3f}, recall {r:.3f}, F1 {f:.3f}")
```

Hand-trace the program and write **every line it prints**, in order, in `answer.txt`. Do not run the code before you have written your answer.

## Example

For `(tp, fp, fn, tn) = (1, 1, 1, 1)` the line would be `name: accuracy 0.500, precision 0.500, recall 0.500, F1 0.500`.

## After you answer

- Which model has the higher accuracy, and which one would you actually use? What does that say about accuracy on imbalanced data?
