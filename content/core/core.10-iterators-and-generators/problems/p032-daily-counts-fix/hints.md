## Hint 1

Run the example by hand with `groupby`. How many groups does it make, and what are their keys?
Does `groupby` collect **all** equal keys, or only the ones that sit next to each other?

## Hint 2

There are two groups with the key `2026-10-05`. What happens to `counts["2026-10-05"]` when
the second group is processed?

## Hint 3

Two possible fixes:

```
# 1. Put equal dates next to each other first:
for day, group in groupby(sorted(records, key=day_of), key=day_of): ...

# 2. Or add to the count instead of replacing it:
counts[day] = counts.get(day, 0) + len(list(group))
```
