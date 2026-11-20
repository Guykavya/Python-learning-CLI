# One policy function, deny by default

Chapter section 7.3 (one policy function, deny by default). Scattered `if user.role == "admin"` lines get out of date and cannot be tested. Put every decision in **one** plain function that knows nothing about HTTP, and test it with a table.

`starter.py` gives you the two dataclasses `User(id, role)` and `Order(id, owner_id, status, total_cents)` and a `can` that allows everything (that is the bug to remove). Write `can(user, action, order=None, *, amount=0) -> bool` in `solution.py`. `user` is `None` for an anonymous caller. The actions are `"read"`, `"cancel"`, `"refund"` and `"list_all"`. These rules are **the only** allowed things:

| Role | Allowed |
|---|---|
| anonymous (`None`) | nothing |
| `customer` | `read` their **own** order (`order.owner_id == user.id`); `cancel` their own order **only while** its status is `"pending"`. Needs an order; no `list_all`, no `refund` |
| `support` | `read` any order; `list_all`; `refund` when an order is given and `amount <= REFUND_LIMIT_FOR_SUPPORT` (10 000 cents); never `cancel` |
| `admin` | `read`, `cancel`, `refund` (any amount) and `list_all` |
| any other role | nothing |

An action that is not in the table (a typo, a new action, `"format_disk"`) is denied for **everybody**, admin included. The last line of the function is `return False`: **deny by default**. A mistake in a rule then makes the app too strict (somebody complains), never too open (nobody notices).

## Example

```python
ada, bo = User(1, "customer"), User(2, "customer")
order = Order(10, owner_id=1, status="pending", total_cents=2500)
can(ada, "cancel", order)       # True: her own, still pending
can(bo, "read", order)          # False: not his
can(None, "read", order)        # False: anonymous
can(ada, "format_disk", order)  # False: unknown action
```
