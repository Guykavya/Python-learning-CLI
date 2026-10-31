## Hint 1

Translate before you rewrite. For each line of the original write one plain sentence: "skip
empty rows and rows whose **first character** is `#`", "split on commas; skip unless exactly
3 parts", ... What exactly is `d[k]`? What are the two numbers in it? When does rounding
happen: per row or once at the end? What is the sort key?

## Hint 2

Then test the quirks on the original, not on your guess. Does `" #x,1,2"` count? (`x[0]` is a
space.) Does `"pen,2.0,3"` count? (`int("2.0")`.) Are spaces around numbers a problem?
(`int(" 2 ")`.) Which exception do `int` and `float` raise on bad text?

```
totals = {}                                   # name -> [quantity, revenue]
for row in rows:
    skip if empty or row starts with "#"
    fields = row.split(",");  skip unless 3 fields
    try: quantity = int(...); price = float(...)
    except ValueError: skip
    skip if quantity <= 0
    name = strip + lower;  add quantity and quantity * price
build (name, qty, round(revenue, 2)) tuples; sort by (-revenue, name)
```
