**1. Silent misuse.** `from_acct` and `to_acct` are both strings, so swapping them is still a
valid call: `transfer(500, "CUR-9", "SAV-1", True)` moves money the wrong way and Python cannot
notice. Likewise `notify` is a bare `True`/`False` in fourth position: a reader cannot tell what
`False` means, and a caller who thinks the fourth parameter is something else (for example a
"dry run" flag) passes the wrong meaning with no error. Even the amount could be swapped with an
account in a careless edit, which would only fail later.

**2. `fee=[]`.** The default list is created once, when `def` runs, and shared by every call that
does not pass a fee. If the body ever appends to it, fees from one transfer leak into the next.
Use `None` (or an immutable value such as `0`) as the default and build any list inside the body.
Here a fee is really a number, so `fee=0` is the natural default.

**3. A better signature.**

```python
def transfer(amount, /, *, source, target, notify=False, fee=0):
```

- `amount` is **positional-only**: it is the one obvious input, and its parameter name is not
  part of the interface, so I can rename it later.
- `source` and `target` are **keyword-only and required** (no defaults): every call must name
  them, so a swap is visible on the page (`source="CUR-9"` reads wrong at once) and cannot happen
  by position.
- `notify` is a **keyword-only flag** with a safe default `False`, so the call says
  `notify=True` instead of a mystery `True`.
- `fee` is **keyword-only** with the immutable default `0`; no shared mutable state.

**4. The calls.**

```python
transfer(500, source="SAV-1", target="CUR-9", notify=True)
transfer(500, source="CUR-9", target="SAV-1")
transfer(250, source="SAV-1", target="CUR-9", fee=10)
```

**5. Rule of thumb.** Allow positional use only for the one or two arguments whose meaning is
obvious from the function name; make everything else, especially flags and several values of the
same type, keyword-only; and never use a mutable default.

Key ideas to check: same-typed positionals can be swapped silently; boolean flags by position are
unreadable; mutable default is shared; `/` and `*` enforce the design; defaults should be
immutable.
