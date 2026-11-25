## Hint 1

Which kind of exception does each version raise? List the failing **cells**: which values break which check, and in
which rows? How does a uniqueness check treat the two rows that share an id? What does `nullable=True` do to a missing age?

## Hint 2

```text
id [1, 2, 2, 4]    -> rows 1 and 2 share the value 2 -> two failure cases (field_uniqueness)
age [20, 80, nan, 17] in 18..75, nullable -> 80 (row 1) and 17 (row 3) fail; the missing value (row 2) is allowed
city [Pune, Goa, Delhi, Pune] in [Pune, Delhi] -> Goa (row 1)
total failure cases = 2 + 2 + 1
sorted set of (column, check) pairs -> alphabetical by column; then per column the sorted row labels
```
