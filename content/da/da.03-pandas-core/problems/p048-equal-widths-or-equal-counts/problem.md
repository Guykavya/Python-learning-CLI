# Equal widths or equal counts?

Chapter section 15.4. Two ways to put numbers into groups. Write two functions.

**`age_bands(s)`**: bins with edges **you choose** (`pd.cut`). Edges `0, 18, 40, 65, inf`, labels
`"youth"`, `"adult"`, `"middle"`, `"senior"`. The bins are **right-closed**, so an age of exactly 18 is `"youth"`,
40 is `"adult"`, 65 is `"middle"`. Include the lower edge too, so age `0` is `"youth"`. A negative or missing age gives
a missing label.

**`spend_quartiles(s)`**: bins with (nearly) **equal numbers of rows** (`pd.qcut`) in four groups labelled
`"Q1"` (lowest) to `"Q4"` (highest). The edges are the quartiles of the data, bins are right-closed with the lowest
value included, so a value exactly on a quartile edge goes to the **lower** group. Missing values stay missing. You may
assume the data have at least four different quartile edges (no heavy ties).

Both functions return a Series with the same index (a `category` Series is fine) and do not change their input.

## Example

```python
import pandas as pd

from solution import age_bands, spend_quartiles

ages = pd.Series([0, 17, 18, 19, 40, 41, 65, 66, -1, None])
print([None if pd.isna(v) else v for v in age_bands(ages)])
spend = pd.Series([10, 20, 30, 40, 50])
print(spend_quartiles(spend).tolist())
```

```text
['youth', 'youth', 'youth', 'adult', 'adult', 'middle', 'middle', 'senior', None, None]
['Q1', 'Q1', 'Q2', 'Q3', 'Q4']
```
