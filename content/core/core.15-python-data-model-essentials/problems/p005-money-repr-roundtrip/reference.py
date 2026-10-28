class Money:
    def __init__(self, cents, currency):
        self.cents = cents
        self.currency = currency

    def __eq__(self, other):
        if not isinstance(other, Money):
            return NotImplemented
        return (self.cents, self.currency) == (other.cents, other.currency)

    def __repr__(self):
        return f"Money({self.cents!r}, {self.currency!r})"

    def __str__(self):
        sign = "-" if self.cents < 0 else ""
        units, rest = divmod(abs(self.cents), 100)
        return f"{sign}{units}.{rest:02d} {self.currency}"
