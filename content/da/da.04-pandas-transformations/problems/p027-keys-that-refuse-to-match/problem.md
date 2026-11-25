# Keys that refuse to match

Chapter section 6.9. When a join matches fewer rows than it should, suspect the keys: an integer id on one side and
text on the other, a trailing space, lower-case letters. Fix the keys **and measure** how much the fix helped, so that
the keys that still fail can be sent back to whoever owns the data.

Write `normalise_keys(left, right, key)`. Both frames have a column named `key` (no missing values). Return a
dictionary:

- `"left"`, `"right"`: **copies** of the frames in which the `key` column is converted to text, with spaces removed
  at both ends and letters in upper case (`10001` → `"10001"`, `" p002"` → `"P002"`). Other columns unchanged.
- `"match_before"`: the share of **left rows** whose key, as given, appears in the right key column (a `float` from
  0 to 1). An integer `10001` does not match the text `"10001"`.
- `"match_after"`: the same share after cleaning both sides.
- `"unmatched"`: the sorted list of the **different** cleaned left keys that still have no match.

Do not change the inputs.

## Example

```python
import pandas as pd

left = pd.DataFrame({"sku": ["P001", " p002", "P004"], "n": [1, 2, 3]})
right = pd.DataFrame({"sku": ["p001", "P002 "], "name": ["tea", "milk"]})
r = normalise_keys(left, right, "sku")
print(r["left"]["sku"].tolist(), r["right"]["sku"].tolist())
print(round(r["match_before"], 3), round(r["match_after"], 3), r["unmatched"])
```

```text
['P001', 'P002', 'P004'] ['P001', 'P002']
0.0 0.667 ['P004']
```
