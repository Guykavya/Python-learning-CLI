# Label or position?

Chapter sections 2.3 and 7.1. A Series has two ways to find a value: by its **label** (`.loc`) and by its **position**
(`.iloc`). When the labels are integers that are *not* `0..n-1`, a bare `s[3]` is a label lookup, and it is easy to
mix the two up.

Write two functions for a Series of prices indexed by product id:

- `price_of(s, label)` returns the price of the product whose id is `label`.
- `nth_price(s, n)` returns the price at position `n` (0 is the first row, `-1` the last), whatever the labels are.

Both return a plain Python `float`.

## Example

```python
import pandas as pd

s = pd.Series([10.0, 20.0, 30.0], index=[2, 0, 1])
price_of(s, 0)      # 20.0   (the row labelled 0)
nth_price(s, 0)     # 10.0   (the first row)
nth_price(s, -1)    # 30.0   (the last row)
```
