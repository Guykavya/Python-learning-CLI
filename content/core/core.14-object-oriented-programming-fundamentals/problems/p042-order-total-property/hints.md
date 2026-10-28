## Hint 1

What does the order really need to **store**? Only the lines, the discount percent and the
"placed" flag. Everything else can be **computed** from those whenever someone asks. Which tool
lets `o.total` (no parentheses) run code each time it is read?

## Hint 2

`discount_percent` needs both a getter and a setter: the setter checks the value and stores it in
`self._discount_percent`. `apply_coupon` should assign `self.discount_percent = ...`, so the same
check runs. Write a tiny helper `_check_open()` that raises `RuntimeError` when the order is placed,
and call it first in every method that changes the order.

## Hint 3

```
@property
def subtotal(self):  return round(sum(price * qty for each line), 2)

@property
def discount(self):  return round(self.subtotal * self.discount_percent / 100, 2)

@property
def shipping(self):
    if no lines or self.subtotal - self.discount >= self.FREE_SHIPPING_FROM: return 0
    return self.SHIPPING

@property
def total(self):     return round(self.subtotal - self.discount + self.tax + self.shipping, 2)
```
