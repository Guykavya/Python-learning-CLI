## Hint 1

For each customer the question is yes/no: "does my id appear anywhere in `orders["customer_id"]`?" Which Series
method answers that for every row at once? How do you flip the answer?

## Hint 2

```text
mask = ~customers["customer_id"].isin(orders["customer_id"])
return customers[mask].reset_index(drop=True)
# merge version: customers.merge(orders[["customer_id"]].drop_duplicates(), how="left", indicator=True)
#                keep _merge == "left_only", drop the extra columns
```
