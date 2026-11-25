# The same question in Polars

Chapter sections 13.2 and 13.3. Answer a familiar question with Polars expressions: *revenue and number of distinct
orders per region, biggest revenue first.*

Write `revenue_by_region_pl(items)`:

- `items` is a **Polars** `DataFrame` with one row per order line and the columns `order_id`, `region`, `channel`,
  `revenue`;
- return a Polars `DataFrame` with exactly the columns `region`, `revenue` (the sum) and `orders` (the number of
  **distinct** `order_id`s), one row per region;
- sorted by `revenue` from largest to smallest; two regions with the same revenue are sorted by `region`
  alphabetically. (Polars' `group_by` does not promise any order of groups, so the sort is what fixes it.)

The tests compare your table with the pandas answer, row by row, through `.to_dicts()`.

## Example

```python
import polars as pl

items = pl.DataFrame({"order_id": [1, 1, 2, 3], "region": ["west", "west", "north", "west"],
                      "channel": ["store", "store", "online", "online"], "revenue": [100.0, 50.0, 90.0, 10.0]})
print(revenue_by_region_pl(items).to_dicts())
```
```text
[{'region': 'west', 'revenue': 160.0, 'orders': 2}, {'region': 'north', 'revenue': 90.0, 'orders': 1}]
```
