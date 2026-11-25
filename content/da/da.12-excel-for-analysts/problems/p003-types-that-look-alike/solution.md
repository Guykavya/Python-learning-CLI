## Approach

Test the special types first (`None`, `bool`, then numbers, then dates, then strings). A string is a "text number" if `float()` accepts it after stripping; an empty string must be handled before that, because `float("")` fails.

## Code

```python
from datetime import date, datetime


def audit_column(ws, col):
    out = {"numbers": 0, "text_numbers": 0, "blanks": 0, "empty_strings": 0, "dates": 0, "other_text": 0, "booleans": 0}
    for r in range(2, ws.max_row + 1):
        v = ws[f"{col}{r}"].value
        if v is None:
            out["blanks"] += 1
        elif isinstance(v, bool):
            out["booleans"] += 1
        elif isinstance(v, (int, float)):
            out["numbers"] += 1
        elif isinstance(v, (datetime, date)):
            out["dates"] += 1
        elif isinstance(v, str):
            if v == "":
                out["empty_strings"] += 1
            else:
                try:
                    float(v.strip())
                    out["text_numbers"] += 1
                except ValueError:
                    out["other_text"] += 1
    return out
```

## Complexity

O(rows).

## Another way

In Excel itself: `COUNT(range)` (numbers) against `COUNTA(range)` (non-empty cells): when they differ, something is text.
