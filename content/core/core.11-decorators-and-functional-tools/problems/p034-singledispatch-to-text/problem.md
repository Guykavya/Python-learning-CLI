# singledispatch: turn any value into text

`functools.singledispatch` picks which function to run from the **type of the first argument**.
You register one small function per type instead of writing a long `if isinstance(...)` chain.

Write `to_text(value)` in `solution.py` with `@singledispatch` and one registered function per
type. It turns a value into a short text, a bit like JSON:

| Value | Result | Notes |
|---|---|---|
| `int` | `"42"` | |
| `float` | `"3.50"` | always two decimals |
| `bool` | `"yes"` / `"no"` | see the trap below |
| `str` | `'"hi"'` | the text in double quotes |
| `None` | `"null"` | register `type(None)` |
| `list` | `'[1, "a"]'` | items converted with `to_text`, joined by `", "` |
| `tuple` | `"(1, 2)"` and `"(7,)"` | a one-item tuple keeps its comma; `()` for empty |
| `dict` | `'{"a": 1}'` | `key: value`, both converted with `to_text`, joined by `", "` |
| anything else | raise `TypeError` | message: `cannot convert set` (use the type's name) |

**The bool trap.** `bool` is a subclass of `int`: `isinstance(True, int)` is `True`. If you only
register `int`, then `to_text(True)` gives `"True"`. Register `bool` separately; `singledispatch`
always picks the **most specific** registered class.

**Example**

```python
to_text([1, "a", None, (2.5,)])      # '[1, "a", null, (2.50,)]'
to_text({"ok": True, "n": [1, 2]})   # '{"ok": yes, "n": [1, 2]}'
to_text({1, 2})                      # TypeError: cannot convert set
```

You may write `@to_text.register(list)` or `@to_text.register` with a type hint on the first
parameter (`def _(value: list):`). Both are fine.
