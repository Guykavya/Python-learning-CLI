# Shrink a frame

Chapter sections 10.4, 10.5 and 17.2. Large tables waste memory on types that are too big. Write `shrink(df)` that
returns a **new** frame with the same values in smaller types:

- **Integer columns** become the smallest **signed** integer type that holds all their values
  (`pd.to_numeric(s, downcast="integer")`).
- **Float columns** become `float32` **only if no value changes** (every value is the same after a trip through
  `float32` and back; missing values stay missing). Otherwise they stay `float64`: this is a memory saving, never a rounding.
- **Text columns** with **at most 50 distinct values** become `category`.
- Booleans, dates and all other columns are left alone.

Every value must stay equal (compare column by column), the index and the column order stay, and the input frame is not
changed. On the test's generated table (numbers, exact decimals, a few cities, a date) the result must use at most half of the original memory
(`memory_usage(deep=True).sum()`). A loop over the **columns** is fine; a loop over rows is not.

## Example

```python
import numpy as np
import pandas as pd

from solution import shrink

df = pd.DataFrame({
    "qty": np.array([1, 5, 7, 3], dtype="int64"),
    "price": [0.5, 0.25, 4.0, 3.75],
    "cost": [0.1, 0.2, 0.3, 0.4],
    "city": ["Pune", "Agra", "Pune", "Agra"],
})
out = shrink(df)
print({c: str(t) for c, t in out.dtypes.items()})
print(out["cost"].tolist() == df["cost"].tolist())
```

```text
{'qty': 'int8', 'price': 'float32', 'cost': 'float64', 'city': 'category'}
True
```
