## Hint 1

Which table's rows must all survive? Put that table on the left. After the merge, how can you tell an order whose
customer was not found: by a missing `city`, or by something more reliable that `merge` can add for you?

## Hint 2

```text
table = orders.merge(customers, on="customer_id", how="left", validate="m:1", indicator=True)
unknown = int((table["_merge"] == "left_only").sum())
return table.drop(columns="_merge"), unknown
check: len(table) == len(orders)
```
