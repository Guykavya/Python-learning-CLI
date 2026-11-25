# Where did the values go?

Chapter sections 10.3, 19.4 and 19.5. Converting a text column with `errors="coerce"` turns bad entries into missing
values **silently**. The audit that finds them compares the raw text with the converted result. Write
`conversion_losses(raw, clean)` where `raw` is a DataFrame of **text** (as read with `dtype=str`) and `clean` is the
converted DataFrame with the **same index and rows**.

It returns a dict with **one entry per column that exists in both frames** (in the order of `raw`'s columns):

```python
{"price": {"lost": 2, "examples": ["free", "n.a."]}, "qty": {"lost": 0, "examples": []}}
```

- `lost`: the number of rows where the raw value was **not empty** (not missing and not just spaces) **but** the clean
  value is missing. Rows that were empty in the raw data are not losses: nothing was lost there.
- `examples`: up to **3 distinct** raw texts of the lost rows, in the order they first appear (the text as given,
  not stripped).

No loops over rows (a loop over the columns is fine). Neither input is changed.

## Example

```python
import pandas as pd

from solution import conversion_losses

raw = pd.DataFrame({"price": ["10", "free", " ", None, "n.a.", "free"], "qty": ["1", "2", "3", "4", "5", "6"]})
clean = pd.DataFrame({"price": pd.to_numeric(raw["price"], errors="coerce"), "qty": pd.to_numeric(raw["qty"])})
print(conversion_losses(raw, clean))
```

```text
{'price': {'lost': 3, 'examples': ['free', 'n.a.']}, 'qty': {'lost': 0, 'examples': []}}
```
