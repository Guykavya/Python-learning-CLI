class CurrencyMismatchError(ValueError):
    """Raised when two Money values with different currencies are combined."""


class Money:
    def __init__(self, cents, currency):
        self.cents = cents
        self.currency = currency

    def __eq__(self, other):
        if not isinstance(other, Money):
            return NotImplemented
        return (self.cents, self.currency) == (other.cents, other.currency)

    def __hash__(self):
        return hash((self.cents, self.currency))

    def __repr__(self):
        return f"Money({self.cents!r}, {self.currency!r})"

    def _check(self, other):
        if self.currency != other.currency:
            raise CurrencyMismatchError(f"cannot mix {self.currency} and {other.currency}")

    def __add__(self, other):
        if not isinstance(other, Money):
            return NotImplemented
        self._check(other)
        return Money(self.cents + other.cents, self.currency)

    def __sub__(self, other):
        if not isinstance(other, Money):
            return NotImplemented
        self._check(other)
        return Money(self.cents - other.cents, self.currency)

    def __mul__(self, n):
        if not isinstance(n, int):
            return NotImplemented
        return Money(self.cents * n, self.currency)

    __rmul__ = __mul__

    def __neg__(self):
        return Money(-self.cents, self.currency)
