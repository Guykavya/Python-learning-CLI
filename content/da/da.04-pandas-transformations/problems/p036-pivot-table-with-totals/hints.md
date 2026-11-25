## Hint 1

`pivot_table` is a groupby plus a pivot. Which arguments choose the aggregation, fill the empty cells, add the totals
and give the total row and column their name?

## Hint 2

```text
items.pivot_table(index="region", columns="month", values="revenue",
                  aggfunc="sum", fill_value=0, margins=True, margins_name="Total")
```
Then check: the bottom-right cell equals items["revenue"].sum().
