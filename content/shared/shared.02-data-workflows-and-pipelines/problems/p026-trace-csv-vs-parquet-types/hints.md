## Hint 1

Do the CSV half first and write the data line by hand: for each of the six values, what is
`str(value)`, and what does `DictWriter` do with `None`? Then ask: when `DictReader` reads that
line back, can it know that `7` was an int or that `False` was a bool? What is the truth value of
a **non-empty** string? What does `+` do with two strings?

## Hint 2

For the Parquet half, the schema decides every type, and `to_pylist()` turns each value back
into the Python type that matches the column type.

```
csv line   : str(7), "007", "" for None, str(Decimal), str(False), str(datetime) joined by ","
csv read   : every field is a str  ->  'False' is a non-empty str, so it is truthy
             "7" + "007" is string concatenation
parquet    : int64 -> int, string -> str / None, decimal128 -> Decimal, bool_ -> bool,
             timestamp(tz=UTC) -> aware datetime in UTC
             Decimal * 2 keeps two decimal places
print(type) of a pyarrow type prints like: decimal128(P, S)   timestamp[unit, tz=ZONE]
```
