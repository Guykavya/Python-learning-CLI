## Hint 1

For the repr, which form rebuilds the object: `Money(12.50 USD)` or `Money(1250, 'USD')`? Check by passing it to `eval`.

## Hint 2

For `__str__`, split cents into whole units and cents with `divmod(abs(cents), 100)`. Format cents with two digits using `:02d`. Add `-` if the amount is negative.

## Hint 3

```
__repr__: "Money(" + repr(cents) + ", " + repr(currency) + ")"
__str__:
    sign = "-" if cents < 0 else ""
    units, rest = divmod(abs(cents), 100)
    return sign + units + "." + two-digit rest + " " + currency
```
