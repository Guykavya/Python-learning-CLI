## Hint 1

How can you deal with the sign separately from the digits? What is `abs(-12)`?

## Hint 2

Build the number part first, with or without the comma:
```
spec = ",." if thousands else "."
digits = format(abs(amount), spec + str(decimals) + "f")
```
`format(value, spec)` is what an f-string does with `{value:spec}`.

## Hint 3

```
sign = "-" if amount < 0 else ""
return sign + currency + " " + digits
```
