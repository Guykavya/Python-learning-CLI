# `Flag` permissions and an `IntEnum` priority

Two enum variants solve two everyday problems.

- **`enum.Flag`**: members are bits that you combine with `|`, test with `in`, remove with `&` and
  `^`. File permissions, feature switches, options.
- **`enum.IntEnum`**: members are also real `int`s, so they compare with numbers and sort. Priorities,
  levels, exit codes.

Write in `solution.py`:

**`Permission(Flag)`** with `READ`, `WRITE`, `EXECUTE`, values from `auto()` (1, 2, 4).

**`Priority(IntEnum)`** with `LOW = 1`, `MEDIUM = 2`, `HIGH = 3`.

And four functions:

- `describe(perm)`: three characters like Unix permissions: `r`, `w`, `x`, or `-` where the flag is
  missing. `READ | EXECUTE` gives `"r-x"`; nothing gives `"---"`.
- `parse(text)`: the opposite. `"rw-"` gives `READ | WRITE`. The text must be exactly three
  characters: each position holds its own letter (`r` at 0, `w` at 1, `x` at 2) or `-`. Anything else
  raises `ValueError`.
- `allows(granted, needed)`: `True` if **every** flag in `needed` is in `granted`.
- `highest(priorities)`: the largest priority of an iterable, or `None` if it is empty.

**Example**

```python
perm = Permission.READ | Permission.WRITE
perm                         # <Permission.READ|WRITE: 3>
describe(perm)               # 'rw-'
parse("r-x")                 # <Permission.READ|EXECUTE: 5>
allows(perm, Permission.READ)                       # True
allows(perm, Permission.READ | Permission.EXECUTE)  # False
Priority.HIGH > 2            # True
highest([Priority.LOW, Priority.HIGH])  # <Priority.HIGH: 3>
```
