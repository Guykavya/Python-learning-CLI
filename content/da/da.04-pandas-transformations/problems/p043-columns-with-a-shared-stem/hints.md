## Hint 1

`pd.wide_to_long` was made for this: what are the *stubs*, what is the *i* (the row id), what will *j* (the new key)
be called, and which separator sits between stub and year?

## Hint 2

```text
out = pd.wide_to_long(df, stubnames=["sales", "units"], i="store_id", j="year", sep="_")
out = out.reset_index()                  (store_id and year come back as columns)
keep the columns store_id, year, sales, units
sort by store_id, year; reset the index
```
