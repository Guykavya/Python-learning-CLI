# Tidy a name column

Chapter sections 12.1 and 12.5. Names typed by hand come with extra spaces and mixed case, which makes the same
person look like several. Write `tidy_names(s)` that takes a Series of text and returns a new Series where each name

1. has no leading or trailing whitespace,
2. has every run of whitespace inside it replaced by **one space**,
3. is in title case (`"asha rao"` becomes `"Asha Rao"`).

Missing values stay missing (they are not turned into the text `"nan"` or `"None"`). Letters outside ASCII
(`é`, `ç`, `ñ`) are kept. The index and the order of rows do not change, and the input is not modified.

## Example

```python
import pandas as pd

from solution import tidy_names

names = pd.Series(["  asha   rao ", "BEN kumar", None, "zoë  çelik"])
print(tidy_names(names).tolist())
print(names.nunique(), tidy_names(names).nunique())
```

```text
['Asha Rao', 'Ben Kumar', nan, 'Zoë Çelik']
3 3
```
