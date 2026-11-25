## Approach

Clean the text in three small steps, then let `to_numeric` judge. Currency words go first (otherwise the dot of `Rs.` stays and `.1250.50` appears); the pattern `(?i)rs\.?|₹|inr` means "Rs with an optional dot, the rupee sign, or INR, in any case". Commas are removed as plain text, which also handles Indian grouping. `strip` removes the spaces. `pd.to_numeric(errors="coerce")` turns anything that is still not a number (`""`, `"-"`, `"free"`, `"n/a"`) into missing, and reads `"-5"` as -5.0.

## Code

```python
import pandas as pd


def to_money(s):
    txt = (s.astype("string").str.replace(r"(?i)rs\.?|₹|inr", "", regex=True)
            .str.replace(",", "", regex=False).str.strip())
    return pd.to_numeric(txt, errors="coerce")
```

## Complexity

O(total characters), a few vectorised passes.

## Another way

Extract with one regex instead: `s.str.extract(r"(-?\d[\d,]*\.?\d*)")[0]`, remove commas, convert. It ignores any junk around the number, which is shorter but also accepts text like `"approx 12 or so"`: the explicit rules above are stricter and safer. Never apply this to European numbers (`1.250,50`): see chapter 12.4.
