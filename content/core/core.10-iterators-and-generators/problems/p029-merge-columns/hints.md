## Hint 1

`zip(*columns)` stops at the shortest column. Which itertools function goes on to the
longest one, and what is its keyword argument for the missing values?

## Hint 2

A row is a tuple like `("Ann", 90, "A")`. `",".join` needs strings. How do you turn each
value into a string inside the join?

## Hint 3

```
for row in zip_longest(*columns, fillvalue=fill):
    yield ",".join(str(value) for value in row)
```
