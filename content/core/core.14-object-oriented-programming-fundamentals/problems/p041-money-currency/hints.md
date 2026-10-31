## Hint 1

Why store `1250` paise instead of `12.5` rupees? Integers are exact; floats are not. So
`from_string` must never go through `float`. How can you get `12` and `"5"` out of `"12.5"` with a
string method? (`str.partition(".")` returns three parts.) How do you turn `"5"` into 50 paise and
`"05"` into 5?

## Hint 2

Read-only properties: store the values in `self._minor` and `self._currency`, and give each a
`@property` getter with no setter. For `split`: `divmod(1000, 3)` is `(333, 1)`. How many parts
should get one extra paisa? For `format`: work with `abs(self.minor)` and put the sign in front
yourself. Why? Try `divmod(-305, 100)` in the REPL.

## Hint 3

```
from_string(cls, text):
    parts = text.split(" "); must be exactly 2
    number, code = parts
    sign = -1 and drop "-" if number starts with "-", else 1
    whole, dot, frac = number.partition(".")
    if whole is not all digits, or (dot and frac is not all digits), or len(frac) > 2: ValueError
    minor = int(whole) * 100 + int(frac.ljust(2, "0"))
    return cls(sign * minor, code)

split(n):
    base, extra = divmod(self.minor, n)
    return [Money(base + 1 if i < extra else base, currency) for i in range(n)]
```
