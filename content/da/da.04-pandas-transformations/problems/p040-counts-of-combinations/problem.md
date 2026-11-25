# Counts of combinations

Chapter section 8.6. The table `orders` has one row per order; it already carries the `region` of the store (merged
earlier) and the `channel` (`"online"` or `"store"`). The manager asks two questions: *how many orders of each channel
in each region?* and *of each region's orders, what share is online?*

Write `channel_by_region(orders)` that returns a pair `(counts, shares)`:

- `counts`: a `crosstab` with one row per region (sorted) and one column per channel (sorted), holding the number of
  orders; a combination that never happens is `0`;
- `shares`: the same table with each **row** divided by its row total, so every row sums to 1.

Do not change the input.

## Example

```python
import pandas as pd

orders = pd.DataFrame({"order_id": [1, 2, 3, 4, 5],
                       "region": ["north", "north", "west", "north", "west"],
                       "channel": ["store", "online", "online", "store", "online"]})
counts, shares = channel_by_region(orders)
print(counts.index.tolist(), counts.columns.tolist())
print(counts.values.tolist())
print(shares.round(3).values.tolist())
```
```text
['north', 'west'] ['online', 'store']
[[1, 2], [2, 0]]
[[0.333, 0.667], [1.0, 0.0]]
```
