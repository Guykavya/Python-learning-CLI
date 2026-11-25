# One city, five spellings

Chapter section 3.1. The raw survey has 32 spellings of 6 cities: `pune`, `" DELHI  "`, `Delhi.`, `Mumbay`. Cheap string
methods fix the *form* (spaces, dots, case); a **mapping table** you write down fixes the *typos*. The last step is a
check: is everything now in the allowed set?

Write `standardise_city(s, mapping)`:

- `s` is a Series of text with possible missing values. `mapping` is a dict from a **normalised key** to the official
  city name, e.g. `{"pune": "Pune", "dehli": "Delhi", "mumbay": "Mumbai"}`.
- **Normalise** each value into a key: strip spaces at both ends, strip **trailing dots**, strip again, replace any run
  of white space inside by **one space**, and make it lower case with `casefold()`.
- The clean value is `mapping[key]`. A key that is **not in the mapping** becomes missing (`NaN`). A missing input stays
  missing.
- Return a tuple `(clean, unmapped)`: `clean` is a Series with the **same index** as `s`, and `unmapped` is the
  **sorted list of distinct keys** (not the original text) that were present but not in the mapping. When everything is
  covered, `unmapped` is `[]`: that empty list is the check.
- Do not change `s`.

## Example

```python
import pandas as pd

mapping = {"pune": "Pune", "delhi": "Delhi", "dehli": "Delhi", "new delhi": "Delhi",
           "mumbai": "Mumbai", "mumbay": "Mumbai"}
s = pd.Series([" PUNE ", "pune", "Delhi.", "Dehli", "Mumbay", "New  Delhi", None, "Goa", "goa.", "Lucknow"])
clean, unmapped = standardise_city(s, mapping)
print(clean.tolist())
print(unmapped)
```

```text
['Pune', 'Pune', 'Delhi', 'Delhi', 'Mumbai', 'Delhi', nan, nan, nan, nan]
['goa', 'lucknow']
```

`Goa` and `goa.` give the same key `goa`, so it is listed once. The missing input is not "unmapped": there was nothing to map.
