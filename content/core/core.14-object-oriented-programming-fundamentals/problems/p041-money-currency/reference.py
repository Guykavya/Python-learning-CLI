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
