## Approach

Reading with `dtype="str"` keeps every cell exactly as written, so the only conversions are the ones you ask for. The four converters follow chapter 18.2: money strips marks and commas then `to_numeric(errors="coerce")`; dates try the formats in order and let `fillna` keep the first match; bools compare the stripped lower-case text with the two word lists; integers go through `to_numeric` and then keep only whole numbers (`num % 1 == 0`) before the cast to `Int64` (a plain `astype("Int64")` on `2.5` raises). Loss accounting is the audit of section 19.4 in one line: a cell the file **had** (`raw.notna()`) that the converter **could not use** (`converted.isna()`). The empty cells and `N/A` were already missing when pandas read the file, so they never count.

## Code

```python
import pandas as pd

TRUE = ("yes", "y", "true", "1")
FALSE = ("no", "n", "false", "0")
FORMATS = ("%Y-%m-%d", "%d/%m/%Y", "%b %d, %Y")


def to_money(s):
    txt = (s.astype("string").str.replace(r"(?i)rs\.?|₹|inr", "", regex=True)
            .str.replace(",", "", regex=False).str.strip())
    return pd.to_numeric(txt, errors="coerce")


def to_date(s):
    text = s.astype("string").str.strip()
    out = pd.Series(pd.NaT, index=s.index, dtype="datetime64[us]")
    for f in FORMATS:
        out = out.fillna(pd.to_datetime(text, format=f, errors="coerce"))
    return out


def to_bool(s):
    t = s.astype("string").str.strip().str.lower()
    out = pd.Series(pd.NA, index=s.index, dtype="boolean")
    out[t.isin(TRUE).fillna(False)] = True
    out[t.isin(FALSE).fillna(False)] = False
    return out


def to_int(s):
    num = pd.to_numeric(s.astype("string").str.strip(), errors="coerce")
    return num.where(num % 1 == 0).astype("Int64")


def load_sales(path, money=(), dates=(), bools=(), ints=()):
    df = pd.read_csv(path, dtype="str", encoding="utf-8")
    losses = {}
    for cols, convert in ((money, to_money), (dates, to_date), (bools, to_bool), (ints, to_int)):
        for c in cols:
            raw = df[c]
            df[c] = convert(raw)
            losses[c] = int((raw.notna() & df[c].isna()).sum())
    return df, losses
```

## Complexity

O(rows x converted columns) for the vectorised conversions, with one pass per date format. The loops run over columns and groups, never over rows.

## Another way

Read with `dtype=` and `converters=`, or `parse_dates`, to convert while reading. That is shorter, but a bad cell then raises or is guessed inside `read_csv` and the loss count is harder to get. Text first, convert second, count the difference is the pattern that keeps every decision visible. Keep the loss dict next to the data: it is the first lines of the problem register in the project.
