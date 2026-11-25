## Hint 1

You want one median per category, but placed on every product row so that `fillna` can line it up by index. Which
groupby method does that? What does the median of a group with no known values come out as?

## Hint 2

```text
median = products.groupby("category")["list_price"].transform("median")   # one value per row
filled = products.assign(list_price = products["list_price"].fillna(median))
known  = products.groupby("category")["list_price"].count()              # known prices per category
unfilled = sorted(categories where known == 0)
```
