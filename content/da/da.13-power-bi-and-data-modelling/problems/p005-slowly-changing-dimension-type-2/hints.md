## Hint 1

Work on a copy. For each change, find the current row of the customer (`IsCurrent`), compare the region, and either do nothing or close it and append a row. Keep a running counter for the next surrogate key.

## Hint 2

```text
out = dim.copy(); nxt = out["SurrogateKey"].max() + 1
for each change: cur = out[(CustomerID == id) & IsCurrent]
  none -> append new row (ValidFrom = as_of)
  same region -> continue
  else: out.loc[cur.index, ["ValidTo","IsCurrent"]] = [as_of - 1 day, False]; append new row; nxt += 1
lookup: rows with CustomerID == id and ValidFrom <= date <= ValidTo
```
