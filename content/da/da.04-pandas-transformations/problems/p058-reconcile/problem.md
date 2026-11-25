# `reconcile`

Chapter section 14.2. Every breakdown of a table (revenue by store, by channel, by month) must add up to the grand
total. If it does not, a row was lost, doubled or left out of a group. `reconcile` checks that in one line.

Write `reconcile(parts, total, label="", tol=0.01, strict=False)` that returns a pair `(ok, difference)`:

- `parts` is anything `pd.Series(...)` accepts: a Series (for example a `groupby` result), a dict or a list of numbers;
- `difference` is `sum(parts) - total`, **rounded to 2 decimals**, as a plain Python `float`, and never `-0.0` (a
  rounded tiny negative difference must come out as `0.0`);
- `ok` is a plain `bool`: `True` when `abs(difference) <= tol`;
- with `strict=True`, a difference larger than `tol` raises `ValueError` with a readable message of the form
  `"<label>: parts=<sum> total=<total> diff=<difference>"`, numbers formatted with thousands separators and 2 decimals
  (for example `"revenue by store: parts=6,216,711.12 total=7,360,844.05 diff=-1,144,132.93"`);
- float noise such as `0.1` added ten times against `1.0` must pass;
- do not change `parts`.

## Example

```python
import pandas as pd

by_store = pd.Series({"S1": 1200.50, "S2": 799.50})
print(reconcile(by_store, 2000.0, "revenue by store"))
print(reconcile([0.1] * 10, 1.0, "noise"))
print(reconcile({"grocery": 700.0, "toys": 250.0}, 1000.0, "by category"))
try:
    reconcile({"grocery": 700.0, "toys": 250.0}, 1000.0, "by category", strict=True)
except ValueError as e:
    print(e)
```
```text
(True, 0.0)
(True, 0.0)
(False, -50.0)
by category: parts=950.00 total=1,000.00 diff=-50.00
```
