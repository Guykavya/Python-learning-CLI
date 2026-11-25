# A priority column with `np.select`

Chapter section 15.3. A collections table has `overdue_days` (whole number), `amount` (number) and `vip` (bool).
Write `priority(df)` that returns a Series named `"priority"` (same index) with the first rule that matches:

1. `overdue_days > 30` gives `"urgent"`;
2. a `vip` customer with `overdue_days > 0` gives `"high"`;
3. `amount >= 5000` gives `"medium"`;
4. anything else gives `"low"`.

**The first matching rule wins**: a VIP who is 40 days overdue is `"urgent"`, not `"high"`. Use `np.select`; no loop.

## Example

```python
import pandas as pd

from solution import priority

df = pd.DataFrame({
    "overdue_days": [40, 3, 0, 0, 10],
    "amount": [100, 100, 6000, 100, 6000],
    "vip": [True, True, False, True, False],
})
print(priority(df).tolist())
```

```text
['urgent', 'high', 'medium', 'low', 'medium']
```
