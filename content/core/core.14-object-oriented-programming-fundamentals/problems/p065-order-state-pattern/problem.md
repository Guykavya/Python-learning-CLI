# Order states as objects (the State pattern)

An online order moves through states: **pending** -> **paid** -> **shipped** -> **delivered**, and it
can be **cancelled** while pending or paid. The usual first version is a string `self.status` and big
`if` chains in every method. With the **State pattern**, every state is a small class that knows which
actions it allows, and the `Order` simply **delegates** to its current state object.

In `solution.py` write:

### `InvalidTransition(Exception)`

`InvalidTransition(state, action)` stores both and has the message
`f"cannot {action} an order that is {state}"`, for example `cannot ship an order that is pending`.

### `OrderState` and its subclasses

`OrderState` is the base class. It has a class attribute `name` and four methods
`pay(self, order)`, `ship(self, order)`, `deliver(self, order)`, `cancel(self, order)`. In the base
class, each of them raises `InvalidTransition(self.name, "<action>")`. A subclass overrides only the
actions it allows; an allowed action **returns the next state object**.

| class | `name` | allowed actions |
|---|---|---|
| `Pending` | `"pending"` | `pay` -> `Paid()`, `cancel` -> `Cancelled()` |
| `Paid` | `"paid"` | `ship` -> `Shipped()`, `cancel` -> sets `order.refunded = True`, returns `Cancelled()` |
| `Shipped` | `"shipped"` | `deliver` -> `Delivered()` |
| `Delivered` | `"delivered"` | none |
| `Cancelled` | `"cancelled"` | none |

### `Order`

- `Order(order_id, initial=None)`: `initial` is the starting state object; `None` means `Pending()`.
  Sets `order_id`, `refunded = False` and the history.
- `state`: a read-only property with the **name** of the current state (`"pending"`).
- `state_object`: a read-only property with the current state **object**.
- `history`: a list of state names, starting with the initial one; every successful action appends
  the new name.
- `pay()`, `ship()`, `deliver()`, `cancel()`: each calls the same-named method of the current state
  with the order (`self._state.pay(self)`), and stores the returned state. A failed action raises
  `InvalidTransition` and changes nothing.
- `can(action)`: `True` if the action (a string such as `"ship"`) would succeed now, else `False`. It
  must not change the order. Do not repeat the transition table in `Order`: ask the state. (Hint: try
  the action on the state object and look at what happens. Watch out: `Paid.cancel` changes
  `order.refunded`, so `can("cancel")` on a paid order must not leave `refunded` set.)
  An unknown action name raises `ValueError(f"unknown action {action!r}")`.

`Order` must not contain an `if`/`elif` chain on state names. The tests plug in a state class you have
never seen, to check that `Order` only delegates.

## Example

```python
o = Order("A1")
o.state                  # 'pending'
o.can("ship")            # False
o.ship()                 # InvalidTransition: cannot ship an order that is pending
o.pay(); o.state         # 'paid'
o.cancel()
o.state, o.refunded      # ('cancelled', True)
o.history                # ['pending', 'paid', 'cancelled']
o.pay()                  # InvalidTransition: cannot pay an order that is cancelled

class Review(OrderState):          # a new state, defined outside your file
    name = "in review"
    def pay(self, order):
        return Paid()

r = Order("B2", initial=Review())
r.state, r.can("cancel")           # ('in review', False)
r.pay(); r.history                 # ['in review', 'paid']
```
