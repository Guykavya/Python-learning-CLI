# ROC-AUC against average precision

Chapter section 9. Two ranking metrics for one list of scores. **ROC-AUC** is the share of (positive, negative) pairs ranked correctly. **Average precision** (AP) walks down the list from the top and averages the precision at each position where a positive appears; it cares most about the top of the list.

```python
labels = [1, 0, 1, 1, 0, 0, 1, 0, 0, 0]
scores = [0.95, 0.90, 0.85, 0.80, 0.70, 0.60, 0.50, 0.40, 0.30, 0.20]

pos = [s for s, l in zip(scores, labels) if l == 1]
neg = [s for s, l in zip(scores, labels) if l == 0]
pairs = sum(1.0 if a > b else 0.5 if a == b else 0.0 for a in pos for b in neg)
auc = pairs / (len(pos) * len(neg))

hits = 0
precisions = []
for k, (s, l) in enumerate(sorted(zip(scores, labels), reverse=True), start=1):
    if l == 1:
        hits += 1
        precisions.append(hits / k)
ap = sum(precisions) / len(pos)

print(f"positives: {len(pos)} of {len(labels)}")
print(f"ROC-AUC: {auc:.3f}")
print(f"precision at each hit: {[round(x, 3) for x in precisions]}")
print(f"average precision: {ap:.3f}")
```

Hand-trace the program and write **every line it prints**, in order, in `answer.txt`. Do not run the code before you have written your answer.

## Example

For `labels = [1, 0]` with scores `[0.9, 0.1]` both metrics are 1: the lines would end with `ROC-AUC: 1.000` and `average precision: 1.000`.

## After you answer

- Move the positive at score 0.50 to the very bottom (score 0.10). Which metric changes more, and why?
