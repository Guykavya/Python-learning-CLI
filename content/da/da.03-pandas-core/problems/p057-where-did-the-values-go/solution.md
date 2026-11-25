## Approach

A conversion loses a value when the input had content but the output has none. Define "had content" on the **raw text**: not missing, and not made only of spaces (`str.strip() != ""`). Then `lost = had_content & clean.isna()`. Because the raw text is an ordinary text column, `text.notna() & (text.str.strip() != "")` can produce `<NA>` for missing entries; `fillna(False)` makes the mask plain. The examples are the raw texts at the lost rows, de-duplicated in first-appearance order and cut at three: `drop_duplicates().head(3)`. A loop over the columns is allowed; every column is handled by vectorised masks.

## Code

```python
import pandas as pd


def conversion_losses(raw, clean):
    out = {}
    for col in [c for c in raw.columns if c in clean.columns]:
        text = raw[col].astype("string")
        non_empty = (text.notna() & (text.str.strip() != "")).fillna(False)
        lost = non_empty & clean[col].isna()
        out[col] = {"lost": int(lost.sum()),
                    "examples": text[lost].drop_duplicates().head(3).tolist()}
    return out
```

## Complexity

O(rows x shared columns): a few vectorised passes per column.

## Another way

Compare counts only: `raw.notna().sum() - clean.notna().sum()` is the net loss per column but misses blanks and cannot show examples, and a column can lose a value and gain another (a clean step that fills). The mask version names the **rows**, which is what the problem register of chapter 19.5 needs: you can then print them and decide what to do.
