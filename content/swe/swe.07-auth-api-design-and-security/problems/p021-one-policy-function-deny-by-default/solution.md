## Approach

```python
def can(user, action, order=None, *, amount=0):
    if user is None:
        return False
    if user.role == "admin":
        return action in {"read", "cancel", "refund", "list_all"}
    if user.role == "support":
        if action in {"read", "list_all"}:
            return True
        if action == "refund":
            return order is not None and amount <= REFUND_LIMIT_FOR_SUPPORT
        return False
    if user.role == "customer":
        if order is None:
            return False
        owns = order.owner_id == user.id
        if action == "read":
            return owns
        if action == "cancel":
            return owns and order.status == "pending"
        return False
    return False                                     # unknown role: deny
```

Each branch ends in an explicit `False`, and so does the function. Allowed things are listed; everything else falls through to denial. The expression `action in {...}` for admin also denies `"format_disk"`: even the most powerful role gets only the actions that were written down. The refund rule shows an attribute-based decision (the amount), and the cancel rule mixes ownership with state (chapter 7.3).

## Complexity

O(1): a few comparisons.

## Another way

Make the rules **data**: a dictionary `{(role, action): predicate}` where each predicate is a small function of `(user, order, amount)`. `can` becomes `predicate = RULES.get((user.role, action)); return bool(predicate and predicate(...))`. The deny-by-default is then `RULES.get(...)` returning `None`. The table is easier to print and to review, at the price of one more level of indirection.
