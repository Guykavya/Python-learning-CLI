## Approach

Tag each piece with its month (`assign` returns a new frame, so the inputs stay untouched), stack all pieces in one
`concat` call with `ignore_index=True`, then put `month` first. `concat` lines columns up **by name**; a column that a
piece lacks becomes `NaN` in its rows.

## Code

```python
import pandas as pd


def stack_months(frames):
    pieces = [frame.assign(month=key) for key, frame in frames.items()]
    out = pd.concat(pieces, ignore_index=True)
    rest = [c for c in out.columns if c != "month"]
    return out[["month"] + rest]
```

## Complexity

O(total rows × columns): `concat` copies every value once. Calling `concat` inside a loop would copy the growing
result again on every pass, O(k²) for k files.

## Another way

`pd.concat(frames, names=["month", None]).reset_index(level=0).reset_index(drop=True)` uses the dictionary keys as an
outer index level (`keys=`) and then turns that level into a column.
