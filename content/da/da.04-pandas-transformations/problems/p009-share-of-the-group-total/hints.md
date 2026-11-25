## Hint 1

You need the store total next to every line, not one row per store. Which groupby method returns one value **per
original row**, with the input's index? Why does that matter when you divide?

## Hint 2

```text
total = lines.groupby("store_id")["revenue"].transform("sum")     # same index as lines
return lines.assign(share = lines["revenue"] / total)
```
