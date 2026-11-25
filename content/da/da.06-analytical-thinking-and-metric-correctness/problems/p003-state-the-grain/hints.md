## Hint 1

For each table, finish the sentence "if I count the rows, I get the number of ...". What real-world thing or moment is
that? Then ask which columns together must be unique for that to be true.

## Hint 2

```text
for each table:
    grain  = "one row per <thing>" (+ "per <day / snapshot / month>" if time is part of it)
    key    = the smallest set of columns that cannot repeat
    shape  = entity | line | event | snapshot | aggregate
    trap   = what a naive len(), sum() or nunique() would count wrongly
```

Look at which tables have a time column as part of the key (snapshot, aggregate by day).
