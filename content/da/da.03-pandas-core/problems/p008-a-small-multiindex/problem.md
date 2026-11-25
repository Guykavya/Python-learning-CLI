# A small MultiIndex

Chapter section 4.4. An index can have two levels, for example `region` and `month`. `loc` then takes a tuple.

`df` has columns `region`, `month`, `sales`. Each (region, month) pair appears at most once. Write:

- `sales_for(df, region, month)` using `set_index(["region", "month"])`: the sales of that pair as an `int`; a pair that
  does not exist gives `0` (no `KeyError`).
- `sales_by_region(df)`: a dict `{region: total sales over all months}`, with regions in sorted order. Use the
  MultiIndex (for a region, `.loc[region]` returns the months below it); `groupby` is not needed.

The input frame is not changed.

## Example

```python
df = pd.DataFrame({"region": ["N", "N", "S"], "month": ["Jan", "Feb", "Jan"], "sales": [10, 12, 7]})
sales_for(df, "N", "Feb")    # 12
sales_for(df, "S", "Feb")    # 0   (no such pair)
sales_for(df, "W", "Jan")    # 0   (no such region)
sales_by_region(df)          # {"N": 22, "S": 7}
```
