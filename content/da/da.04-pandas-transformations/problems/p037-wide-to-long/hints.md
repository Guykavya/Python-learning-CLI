## Hint 1

`melt` keeps the `id_vars` columns and turns every other column into rows. Which two arguments name the new columns
(the old column names, and the cell values)? After melting, in what order are the rows?

## Hint 2

```text
long = wide.melt(id_vars="store_id", var_name="month", value_name="sales")
sort by ["store_id", "month"]  ("YYYY-MM" text sorts like the calendar)
reset the index (drop the old one)
```
