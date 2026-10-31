## Approach

The truth test `bool(x)` follows this order (chapter section on container protocols and truthiness):

1. If the class defines `__bool__`, call it. It must return `True` or `False` (anything else is a `TypeError`).
2. Otherwise, if it defines `__len__`, the object is true when the length is not zero.
3. Otherwise the object is true.

Line by line:

- `Plain()` has neither: yes. `Bag(0)` has only `__len__` with 0: no. `Bag(3)`: yes.
- `Flag(False, 5)`: `__bool__` returns `False` and `__len__` is ignored: no. `Flag(True, 0)`: `__bool__` wins: yes.
- `bool(Bag(2))` is `True`, `bool(Flag(True, 0))` is `True`, `not Bag(0)` is `True`.
- `len(Flag(False, 5))` calls `__len__` directly: `5`.
- `Bag(0) or "fallback"`: `Bag(0)` is false, so `or` returns the second operand: `fallback`.
- `Bag(4) and "second"`: `Bag(4)` is true, so `and` returns the second operand: `second`.
- `Bag(0) or Bag(0)`: both false, `or` returns the last operand, a `Bag`.
- The built-in values: `0`, `0.0`, `""`, `[]`, `{}`, `None` are false; `"0"` (non-empty string) and `[0]` (non-empty list) are true.
- `any([Bag(0), Bag(0)])` False; `any([Bag(0), Bag(1)])` True; `all([Plain(), Bag(1)])` True.
- `bool(Bad())`: `__bool__` returned an int, so `TypeError: __bool__ should return bool, returned int`.
- `len(Plain())`: no `__len__`: `TypeError: object of type 'Plain' has no len()`.

## Another way

Run the program, then change one thing at a time (remove `__bool__` from `Flag`, add `__bool__` to `Bag`) and predict again.
