# Macro, micro and weighted

Chapter section 12. With more than two classes there is one F1 score **per class** (treating that class as positive, all others as negative). Three ways to average them:

- **macro**: the plain mean of the per-class F1 (every class counts the same, however rare)
- **weighted**: the mean weighted by the number of true rows of each class (the *support*)
- **micro**: pool the counts of all classes first (`TP`, `FP`, `FN` summed over classes), then compute one F1 from the pooled counts

A class that is never predicted (or has no true rows) has an F1 of **0.0** (no warning).

Write `multiclass_f1(y, p)` returning a dict `{"macro": ..., "micro": ..., "weighted": ...}` of plain floats. `y` and `p` are 1-D arrays of class labels of the same length (else `ValueError`). Classes are all labels that appear in `y` **or** `p`.

## Example

```text
y = [0,0,0,0,0,0,1,1,2]; p = [0,0,0,0,0,0,1,0,0]
multiclass_f1(y, p)   ->  macro 0.51, micro 0.78, weighted 0.72      (they differ: class 2 is never found)
```
