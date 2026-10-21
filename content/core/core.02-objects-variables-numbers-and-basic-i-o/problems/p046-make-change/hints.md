## Hint 1

In the starter, `100:` for 1234.75 prints 12. Why? Which amount should the 100s be counted from?

## Hint 2

`count, rest = divmod(rest, 50000)` gives the number of 500-rupee notes **and** what remains.
Feed `rest` into the next step.

## Hint 3

```
rest = int(Decimal(input()) * 100)
n500, rest = divmod(rest, 50000)
n100, rest = divmod(rest, 10000)
... and so on down to 100 paise
print("paise:", rest)
```
