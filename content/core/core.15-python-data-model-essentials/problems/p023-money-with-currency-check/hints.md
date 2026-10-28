## Hint 1

Which two different kinds of wrong operand are there? (1) not a Money at all, (2) a Money in another currency. Which one should return `NotImplemented` and which should raise your own error?

## Hint 2

In `__add__` first check `isinstance(other, Money)` (else `NotImplemented`), then compare currencies and raise `CurrencyMismatchError(f"cannot mix {a} and {b}")`. A helper `_check(self, other)` avoids repeating the code in `__sub__`.

## Hint 3

```
__add__(self, other):
    not Money -> NotImplemented
    self.currency != other.currency -> raise CurrencyMismatchError("cannot mix USD and EUR")
    return Money(self.cents + other.cents, self.currency)
__sub__: same with -
__mul__(self, n): n must be an int (not bool? either way) -> else NotImplemented ; Money(cents * n)
__rmul__ = __mul__ ; __neg__: Money(-cents, currency)
```
