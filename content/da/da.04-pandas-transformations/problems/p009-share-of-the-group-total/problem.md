# Share of the group total

Chapter section 4.1. `transform("sum")` puts the group total **on every row**, with the same index as the input, so
it can be divided straight into a column. That is the everyday "percent of the group total".

Write `share_of_store(lines)`. `lines` has columns `order_id`, `store_id` and `revenue`, and any index. Return a
**new** frame: the same rows, in the same order, with the same index, plus a column `share` = the line's revenue
divided by the total revenue of **its store**. In each store the shares add up to 1. Do not change `lines`.

## Example

```python
import pandas as pd

lines = pd.DataFrame({"order_id": [1, 2, 3, 4],
                      "store_id": ["S1", "S2", "S1", "S1"],
                      "revenue": [10.0, 50.0, 30.0, 60.0]}, index=[7, 8, 9, 10])
print(share_of_store(lines))
```

```text
    order_id store_id  revenue  share
7          1       S1     10.0    0.1
8          2       S2     50.0    1.0
9          3       S1     30.0    0.3
10         4       S1     60.0    0.6
```
