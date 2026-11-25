## Approach

Think of cost per row and of readability. A vectorised expression has no Python code per row, so it is fast and short. `map` does a look-up. `apply` is the general fall-back for logic that cannot be written for a whole column. Compare with `answer.md` and tick the checklist.

## Code

```python
import pandas as pd

codes = pd.Series(["PUN-2025-0042", "DEL-2025-0007"])

def parse(code):                          # branching logic per value
    site, _, seq = code.split("-")
    return pd.Series({"site": site, "seq": int(seq)})

print(codes.apply(parse).values.tolist())  # [['PUN', 42], ['DEL', 7]]
# for this simple shape the vectorised version is better:
print(codes.str.split("-", expand=True)[[0, 2]].values.tolist())
```

## Complexity

`apply` and `map` with a function are O(n) Python calls (each call has a big constant). A vectorised operation is O(n) inside compiled code, tens to thousands of times faster per row.

## Another way

If a per-row function is unavoidable and slow, call it once per **distinct** value and map the result back: `lookup = {c: f(c) for c in s.unique()}; s.map(lookup)`. With few distinct values that is almost as fast as a vectorised call.
