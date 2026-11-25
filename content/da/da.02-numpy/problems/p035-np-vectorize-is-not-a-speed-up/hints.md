## Hint 1

Count the function calls. How many times is `shipping_fee` called for two million weights? Where does each call run: in C, or in the Python interpreter? Re-read the first paragraph of Ch. 12.3.

## Hint 2

```text
if weight <= 1.0       ->  mask  w <= 1.0
elif weight <= 5.0     ->  mask  w <= 5.0  (checked after the first)
else                   ->  default
np.select([mask1, mask2], [value1, value2], default=value3)
prove: time both (best of several runs) + np.allclose(old, new)
```
