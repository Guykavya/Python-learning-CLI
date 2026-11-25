# Categories to flags

Chapter section 8.8. A model wants numbers, not text: one 0/1 column per channel (**one-hot encoding**).

Write `channel_flags(orders)`:

- the `channel` column is replaced by one column per channel value, named `ch_<value>` (for example `ch_online`),
  holding the integers `1` (this row's channel) or `0`;
- the flag columns come after the other columns, in alphabetical order of the channel; the other columns keep their
  order and values;
- every channel value in the data gets a column (there may be more than two), and each row's flags sum to 1;
- do not change the input.

## Example

```python
import pandas as pd

orders = pd.DataFrame({"order_id": [1, 2, 3], "channel": ["store", "online", "store"]})
out = channel_flags(orders)
print(list(out.columns))
print(out.values.tolist(), out["ch_store"].dtype)
```
```text
['order_id', 'ch_online', 'ch_store']
[[1, 0, 1], [2, 1, 0], [3, 0, 1]] int64
```
