## Approach

A large relative gap means the model fits the training rows much better than new rows (variance). A small gap with an error far above the floor means the model cannot even fit the training rows well (bias).

## Code

```python
def diagnose(lc, task="regression", floor=None):
    if task not in ("regression", "classification"):
        raise ValueError(f"unknown task {task!r}")
    last = lc.iloc[-1]
    error = (1 - last["validation"]) if task == "classification" else last["validation"]
    rel_gap = last["gap"] / max(abs(error), 1e-12)
    if rel_gap > 0.15:
        return "high variance"
    if floor is not None and error > 1.25 * floor:
        return "high bias"
    return "fine"
```

## Complexity

O(1).

## Another way

Look at the whole curve: a gap that is still shrinking at the last size says that more data would help, even if the gap is currently moderate.
