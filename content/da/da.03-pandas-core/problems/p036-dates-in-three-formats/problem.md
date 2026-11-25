# Dates in three formats

Chapter sections 13.1, 13.2 and 18.2. A column mixes date styles: `2025-03-01`, `01/03/2025` and `Mar 1, 2025`. No
single `format=` fits all rows. Write `parse_dates(s, formats)` that returns a **pair** `(parsed, unparsed)`:

- `parsed`: a datetime Series with the same index as `s`. For each row, try the formats **in the order given** and use
  the first that matches the whole text (a format that matches only part of the text does not count). Surrounding
  spaces are ignored. A row no format matches is `NaT`, and so is a missing input.
- `unparsed`: a **list** of the original texts (as given, in row order) that were **not missing** but matched no format.

The order of `formats` is how an ambiguous text is decided: `"01/02/2024"` is 1 February with
`["%d/%m/%Y", "%m/%d/%Y"]` and 2 January with the two formats swapped. Use `pd.to_datetime(..., format=f, errors="coerce")`
once per format and combine the results; do not guess the format. The input Series is not changed.

## Example

```python
import pandas as pd

from solution import parse_dates

raw = pd.Series(["2025-03-01", "01/03/2025", "Mar 1, 2025", "31/02/2025", None, "13/02/2025"])
formats = ["%Y-%m-%d", "%d/%m/%Y", "%b %d, %Y"]
parsed, bad = parse_dates(raw, formats)
print(parsed.dt.strftime("%Y-%m-%d").tolist())
print(bad)
print(parse_dates(pd.Series(["01/02/2024"]), ["%m/%d/%Y", "%d/%m/%Y"])[0].dt.strftime("%Y-%m-%d").tolist())
```

```text
['2025-03-01', '2025-03-01', '2025-03-01', nan, nan, '2025-02-13']
['31/02/2025']
['2024-01-02']
```
