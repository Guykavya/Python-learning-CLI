## Hint 1

Which argument of `json_normalize` says "make one row per element of this list"? Which argument copies the order's own fields onto each row, and how do you reach a field inside a nested object? What happens to a key that is absent in some records, and which argument controls that?

## Hint 2

```text
flat = pd.json_normalize(records,
                         record_path="items",
                         meta=["id", ["customer", "name"]],     # nested path = list
                         errors="ignore")                       # absent meta key -> missing
rename "customer.name" -> "customer"
id -> int64
reindex(columns=[id, customer, sku, qty]): a column no record had is created as missing
```
