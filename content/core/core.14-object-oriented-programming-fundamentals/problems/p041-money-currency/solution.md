## Approach

**A value object.** A `Money` is a value, like a number: once made, it never changes. Every
operation returns a new `Money` (chapter sections 2 and 8). That makes it safe to share: nobody can
change "your" 12.50 behind your back. Read-only properties enforce it: `minor` and `currency` have
getters and no setters, so assignment raises `AttributeError`.

**Integers, not floats.** Money is stored in minor units as an `int`. `from_string` splits the text
with `partition(".")` and builds the number from the digits, so `"0.29"` is exactly 29.

**An alternative constructor.** `from_string` is a classmethod that ends with `cls(...)`, so the
checks in `__init__` run, and subclasses get their own type (section 6).

**A custom exception that fits in.** `CurrencyMismatchError` inherits from `ValueError`: it is a
special kind of "bad value". Code that already catches `ValueError` keeps working, and new code can
catch the precise error (section 17).

**Exact splitting.** `divmod(minor, n)` gives the base part and the leftover paise. The first
`extra` parts get one more paisa, so the parts add up exactly and differ by at most 1.

## Code

```python
class CurrencyMismatchError(ValueError):
    def __init__(self, left, right):
        self.left = left
        self.right = right
        super().__init__(f"cannot combine {left} and {right}")


def _valid_code(code):
    return isinstance(code, str) and len(code) == 3 and all("A" <= ch <= "Z" for ch in code)


class Money:
    def __init__(self, minor, currency):
        if not isinstance(minor, int):
            raise TypeError(f"minor must be an int, got {type(minor).__name__}")
        if not _valid_code(currency):
            raise ValueError(f"currency must be 3 capital letters, got {currency!r}")
        self._minor = minor
        self._currency = currency

    @property
    def minor(self):
        return self._minor

    @property
    def currency(self):
        return self._currency

    @classmethod
    def from_string(cls, text):
        parts = text.split(" ")
        if len(parts) != 2:
            raise ValueError(f"expected '<amount> <CUR>', got {text!r}")
        number, code = parts
        sign = 1
        if number.startswith("-"):
            sign = -1
            number = number[1:]
        whole, dot, frac = number.partition(".")
        if not whole.isdigit() or (dot and not frac.isdigit()) or len(frac) > 2:
            raise ValueError(f"bad amount in {text!r}")
        minor = int(whole) * 100 + int(frac.ljust(2, "0"))
        return cls(sign * minor, code)

    def _check(self, other):
        if not isinstance(other, Money):
            raise TypeError(f"expected Money, got {type(other).__name__}")
        if other.currency != self.currency:
            raise CurrencyMismatchError(self.currency, other.currency)

    def add(self, other):
        self._check(other)
        return Money(self.minor + other.minor, self.currency)

    def subtract(self, other):
        self._check(other)
        return Money(self.minor - other.minor, self.currency)

    def times(self, factor):
        if not isinstance(factor, int):
            raise TypeError(f"factor must be an int, got {type(factor).__name__}")
        return Money(self.minor * factor, self.currency)

    def split(self, n):
        if not isinstance(n, int) or n < 1:
            raise ValueError(f"n must be a whole number of at least 1, got {n!r}")
        base, extra = divmod(self.minor, n)
        return [Money(base + 1 if i < extra else base, self.currency) for i in range(n)]

    def format(self):
        sign = "-" if self.minor < 0 else ""
        whole, frac = divmod(abs(self.minor), 100)
        return f"{sign}{whole}.{frac:02d} {self.currency}"

    def __repr__(self):
        return f"Money({self.minor}, {self.currency!r})"
```

Why `abs` in `format`? Python's `divmod(-305, 100)` is `(-4, 95)`, because `//` rounds down. That
would print `-4.95`. Working with the absolute value and adding the sign gives `-3.05`.

`"".isdigit()` is `False`, so `". INR"` and `"12. INR"` are rejected without extra code.

## Complexity

All operations are O(1), except `split(n)` (O(n)) and `from_string` (O(length of the text)).

## Another way

`add` and `subtract` create `Money(...)` by name, so a subclass gets a plain `Money` back.
`type(self)(...)` would keep the subclass. The `decimal` module (`Decimal("0.29") * 100` is exact) is
another safe tool for money. Later, in core.15, you will see how to write `a + b` instead of
`a.add(b)` (`__add__`) and how to make `Money(5, "INR") == Money(5, "INR")` true (`__eq__`).
