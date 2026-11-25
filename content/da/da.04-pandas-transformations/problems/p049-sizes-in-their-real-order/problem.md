# Sizes in their real order

Chapter section 10.2. Text sorts alphabetically: `L, M, S, XL`. Clothing sizes have a real order: `S < M < L < XL`.
An **ordered categorical** knows it. It also has a closed list of allowed values, so anything else (a typo, a size the
shop does not sell) becomes missing, silently.

Write `sort_by_size(df)` that returns a pair `(out, n_unknown)`:

- `df` has a text column `size` (and other columns). Only `"S"`, `"M"`, `"L"`, `"XL"` are valid, compared exactly;
- `out` is a copy of `df` whose `size` column is an **ordered** categorical with the categories `["S", "M", "L", "XL"]`,
  rows sorted by size (rows with the same size keep their original order), invalid and missing sizes last (in their
  original order), fresh index;
- `n_unknown` is the number of rows whose size was **present but invalid** (a missing size is not counted);
- pandas 3 warns (`Pandas4Warning`) when you convert values that are not in the categories, and a future version will
  raise. Make invalid values missing **before** converting, so no such warning appears;
- do not change the input.

## Example

```python
import pandas as pd

df = pd.DataFrame({"item": [1, 2, 3, 4, 5], "size": ["M", "XS", "S", "L", None]})
out, n_unknown = sort_by_size(df)
print(out["item"].tolist(), out["size"].tolist(), n_unknown)
print(out["size"].cat.categories.tolist(), out["size"].cat.ordered)
```
```text
[3, 1, 4, 2, 5] ['S', 'M', 'L', nan, nan] 1
['S', 'M', 'L', 'XL'] True
```
