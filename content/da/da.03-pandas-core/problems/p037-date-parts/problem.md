# Date parts

Chapter section 13.3. Write `add_date_parts(df, col)` that returns a **new** DataFrame with five columns added at the
end, made from the datetime column named `col`:

| column | meaning |
|---|---|
| `year` | the year |
| `month` | the month number 1 to 12 |
| `quarter` | the quarter 1 to 4 |
| `weekday` | the weekday **name** (`"Monday"` ... `"Sunday"`) |
| `is_weekend` | `True` for Saturday and Sunday, otherwise `False` |

A missing date (`NaT`) gives missing `year`, `month`, `quarter` and `weekday`, and `is_weekend` is `False`. The input
frame is not changed. No loops.

## Example

```python
import pandas as pd

from solution import add_date_parts

df = pd.DataFrame({"when": pd.to_datetime(["2025-03-01", "2025-12-31", None])})
out = add_date_parts(df, "when")
print(out.columns.tolist())
print(out["weekday"].tolist())
print(out["is_weekend"].tolist())
print(out["quarter"].tolist())
```

```text
['when', 'year', 'month', 'quarter', 'weekday', 'is_weekend']
['Saturday', 'Wednesday', nan]
[True, False, False]
[1.0, 4.0, nan]
```
