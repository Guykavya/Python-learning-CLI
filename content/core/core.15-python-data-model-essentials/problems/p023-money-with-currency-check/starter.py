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

    # TODO: __add__, __sub__ (CurrencyMismatchError on different currencies),
    #       __mul__, __rmul__ (int only), __neg__
