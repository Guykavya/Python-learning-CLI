## Approach

Two checks on one interval. They can disagree, which is the lesson: a significant result can be not worth it, and a non-significant one can be inconclusive rather than "no effect".

## Code

```python
def classify(lo, hi, mei=0.5):
    if lo > mei:
        label = "worth it: the whole interval is above the minimum effect"
    elif hi < mei:
        label = "not worth it: the whole interval is below the minimum effect"
    else:
        label = "inconclusive: the interval contains the minimum effect"
    return label, bool(lo > 0 or hi < 0)
```

## Complexity

O(1).

## Another way

Write the MEI down **before** the analysis, with the cost of the change; otherwise the threshold drifts to fit the result.
