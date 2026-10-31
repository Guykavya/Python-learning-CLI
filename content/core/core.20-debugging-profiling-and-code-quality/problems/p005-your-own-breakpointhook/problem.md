# Your own breakpointhook

`breakpoint()` does not start pdb by itself. It calls **`sys.breakpointhook(*args, **kwargs)`**,
and the default hook (kept safe in `sys.__breakpointhook__`) starts pdb. Replace the hook and
every `breakpoint()` in the program does something else. That is how `PYTHONBREAKPOINT` and
IDE debuggers plug in.

Write two functions in `solution.py`:

**`install_recorder() -> list[dict]`**

- Creates a new empty list `records` and sets `sys.breakpointhook` to a function that, each
  time `breakpoint()` is called, appends one dict to `records`:
  `{"function": <name of the function that called breakpoint()>, "locals": <a copy of its local variables>}`.
- The hook must accept and ignore any arguments (`breakpoint(1, x=2)` passes them on).
- Returns `records`. The **same** list keeps growing as more `breakpoint()` calls happen.
- The `"locals"` value must be a **snapshot**: a new `dict` taken at the moment of the call,
  so later changes to the variables do not show up in old records.

**`uninstall() -> None`**: puts the original hook back: `sys.breakpointhook = sys.__breakpointhook__`.

Hint for the hook: inside it, `sys._getframe(1)` is the frame of the code that called
`breakpoint()` (the built-in itself has no Python frame). A frame has `.f_code.co_name` and
`.f_locals`.

**Example**

```python
def average(xs):
    total = sum(xs)
    breakpoint()
    total = total / len(xs)
    breakpoint()
    return total

records = install_recorder()
average([2, 4, 9])
uninstall()
records
# [{'function': 'average', 'locals': {'xs': [2, 4, 9], 'total': 15}},
#  {'function': 'average', 'locals': {'xs': [2, 4, 9], 'total': 5.0}}]
```

No pdb prompt ever appears: the recorder replaced it.
