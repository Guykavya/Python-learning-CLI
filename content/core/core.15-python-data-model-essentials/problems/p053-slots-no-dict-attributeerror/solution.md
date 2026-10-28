## Approach

Rules (chapter section on `__slots__`):

1. A class with `__slots__` and no `__dict__` slot stores attributes only in its slots. Assigning another name raises `AttributeError`.
2. A slot is a descriptor on the class (`type(P.x).__name__` is `member_descriptor`); each object has a storage cell for it. If the cell was never assigned (or was deleted) reading raises `AttributeError`.
3. A subclass that does not declare `__slots__` gets a `__dict__`. One that does declare it adds only the new slots.
4. Listing `"__dict__"` in `__slots__` adds a normal dict back.

Line by line:

- `print(p.x)` prints `1`.
- `p.y`: the slot exists but was never assigned: `1 AttributeError 'P' object has no attribute 'y'`.
- `p.z = 3`: no such slot and no dict: `2 AttributeError`.
- `hasattr(...)` for `p`, `Q(1)`, `R(1)`: `False True False`.
- `q.extra = "ok"` works (Q has a dict): `ok 2`.
- `r.z = 4` works (slot of R): `3 4`. `r.w = 0` fails: `3 AttributeError`.
- `S`: `s.a = 1` (slot), `s.anything = 2` (goes to the dict). `vars(s)` shows only the dict: `1 2 {'anything': 2}`.
- `vars(p)`: `4 TypeError vars() argument must have __dict__ attribute`.
- `del p.x` empties the slot, then `p.x` fails: `5 AttributeError`.
- `P.__slots__` is `('x', 'y')`; `type(P.x).__name__` is `member_descriptor`.

## Another way

Run the code, then add `"y"` assignment to `P.__init__`, or remove `__slots__` from `P`, and predict the new output.
