class Money:
    def __init__(self, cents, currency):
        self.cents = cents
        self.currency = currency

    def __eq__(self, other):
        if not isinstance(other, Money):
            return NotImplemented
        return (self.cents, self.currency) == (other.cents, other.currency)

    # TODO: __repr__  -> Money(1250, 'USD')
    # TODO: __str__   -> 12.50 USD   (negative: -0.05 EUR)
