# Map codes to names

Chapter section 15.2. A column holds region **codes** (`"N"`, `"S"`, ...). Write `map_regions(s, mapping)` that returns
a pair `(names, unknown)`:

- `names`: a Series with the same index in which every code is replaced by `mapping[code]`. A code that is **not in**
  the mapping becomes the text `"Other"`. A **missing** code stays missing (it is not "Other").
- `unknown`: a **sorted list** of the distinct codes that were not in the mapping (missing values are not codes, so
  they are not listed).

Use `Series.map` with the dictionary; no loop. The input Series is not changed.

## Example

```python
import pandas as pd

from solution import map_regions

codes = pd.Series(["N", "S", "X", "E", "X", None, "Z"])
names, unknown = map_regions(codes, {"N": "North", "S": "South", "E": "East"})
print(names.tolist())
print(unknown)
```

```text
['North', 'South', 'Other', 'East', 'Other', nan, 'Other']
['X', 'Z']
```
