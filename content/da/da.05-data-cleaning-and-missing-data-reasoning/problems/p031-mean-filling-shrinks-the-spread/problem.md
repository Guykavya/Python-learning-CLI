# Mean filling shrinks the spread

Chapter section 9.4. Filling every gap with the mean protects the **mean** and damages the **spread**: a block of rows
now sits at one value, so the standard deviation falls (variance shrinkage).

Write `fill_with_mean(s)`:

- `s` is a numeric Series, possibly with missing values.
- Return `(filled, sd_before, sd_after)`:
  - `filled`: a **new** Series where each missing value is replaced by the mean of the **observed** values (same index
    and name);
  - `sd_before`: the standard deviation of `s` (`s.std()`, missing values skipped, `ddof=1`), as a `float`;
  - `sd_after`: the standard deviation of `filled`, as a `float`.
- If nothing is missing, `filled` equals `s` and the two standard deviations are equal. Do not change `s`.

## Example

```python
import numpy as np
import pandas as pd

filled, before, after = fill_with_mean(pd.Series([1, 2, 3, np.nan]))
print(filled.tolist())
print(before, round(after, 4))
```

```text
[1.0, 2.0, 3.0, 2.0]
1.0 0.8165
```

The mean of 1, 2, 3 is 2. The new value 2 sits right at the centre, so the spread shrinks from 1.0 to 0.8165.
