## Hint 1

What does `pd.DataFrame(records)` do with the order of the columns and with a key that is missing in some dictionaries? Which argument fixes the column order? Then, which `astype` or conversion function gives each dtype of the table in the statement?

## Hint 2

```text
df = pd.DataFrame(records, columns=COLUMNS)    # fixed order; absent keys -> missing
order_id   -> astype("int64")
customer   -> astype("str")
order_date -> pd.to_datetime(df["order_date"])
qty        -> astype("Int64")     # nullable: the gap does not turn it into float
price      -> astype("float64")
```
