1. **Mutable default argument.** The list `[]` is created once, when `def` runs, and shared by
   every call that omits `tags`. `add_tag("a")` then `add_tag("b")` returns `['a', 'b']` the
   second time: a hidden state that leaks between callers. Fix: use `None` as the default and
   create the list inside: `def add_tag(tag, tags=None): tags = [] if tags is None else tags`.

2. **Bare `except`.** It catches everything, including `KeyboardInterrupt` and `SystemExit`, and
   hides typos (a misspelt name raises `NameError` and silently becomes `0.0`). Bugs become
   invisible. Fix: catch only what you expect, `except ValueError:` (and `TypeError` if
   `text` may be `None`).

3. **Type check with `type(x) == list`.** It rejects subclasses and tuples, is not how Python
   expects you to ask, and a function returning a list-or-number is a mixed contract. Fix: use
   `isinstance(x, list)`, or better, accept any iterable and drop the type test; do not
   return different kinds of thing.

4. **String building with `+=` in a loop.** Strings are immutable, so each `+=` can copy the
   whole text, which gets slow for big inputs, and the line is noisy. Fix: collect parts and join:
   `report = "".join(f"{row.name}: {row.score}\n" for row in rows)`.

5. **Meaningless name `l` (and a loop that is a filter).** `l` looks like `1` or `I`, and says
   nothing about the content. The loop is a comprehension in disguise. Fix:
   `paid_orders = [o for o in orders if o.paid]`.

6. **Returning mixed types (`User` or `False`).** The caller must remember to test the result,
   and a user object that is falsy would be confused with "not found". Fix: return `None`
   (and test with `is None`), or raise `LookupError`, or make the caller pass a default:
   `next((u for u in users if u.name == name), None)`.
