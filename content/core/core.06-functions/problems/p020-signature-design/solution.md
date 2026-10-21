See the model answer shown when you check. The ideas that must appear:

1. Same-typed positional parameters (`from_acct`, `to_acct`) can be swapped silently; a bare `True` flag is unreadable.
2. `fee=[]` is evaluated once and shared; use `None` or an immutable value such as `0`.
3. Keyword-only (after `*`) for the accounts and flags; positional-only (before `/`) for the obvious amount.
4. The calls name `source=` and `target=`, and use `notify=True` instead of a bare `True`.
5. Rule: position only for obvious essentials, names for everything that could be confused.
