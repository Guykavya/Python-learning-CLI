## Hint 1

`on=` needs the same name on both sides. Which two arguments let you name the key separately for each table? After the
merge, which two columns hold the same store id? And what will pandas call the two `city` columns unless you tell it?

## Hint 2

```text
out = orders.merge(stores, left_on="store_id", right_on="sid", how="left",
                   suffixes=("_customer", "_store"), validate="m:1")
out = out.drop(columns="sid")
check: len(out) == len(orders)
```
