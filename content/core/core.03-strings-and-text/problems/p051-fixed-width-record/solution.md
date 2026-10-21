## Code

```python
record = input()
acc = int(record[0:6])
name = record[6:26].strip()
city = record[26:36].strip()
paise = int(record[36:46])
print(f"ID: {acc}")
print(f"Name: {name}")
print(f"City: {city}")
print(f"Amount: Rs {paise // 100:,}.{paise % 100:02}")
```

## Why slices are perfect here

Each slice `record[a:b]` takes exactly `b - a` characters, and the end of one field is the start of the next, so the table translates directly into code. Naming the slices (for example `NAME = slice(6, 26)`) makes larger record formats easier to maintain.

## Why integers for money

`123456 / 100` is a float; it usually prints correctly with `.2f`, but floats cannot store most decimal fractions exactly (core.02). `//` and `%` give exact rupees and paise. `:02` keeps `5` paise as `05`.

## Another way

`Decimal(paise) / 100` with `:,.2f` from the `decimal` module also gives exact output.
