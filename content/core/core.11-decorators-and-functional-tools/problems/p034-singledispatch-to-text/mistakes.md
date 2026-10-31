- Registering only `int` and getting `"True"` for `True`.
- Calling `str(item)` for the items of a list instead of `to_text(item)`. Nested values then
  come out in Python's format, for example `'a'` instead of `"a"`.
- Returning `str(value)` in the fallback. Unknown types should fail loudly with `TypeError`.
- `register(None)` instead of `register(type(None))`. `register` needs a class.
- Forgetting the comma in a one-item tuple: `(7)` is just the number 7 in brackets.
- Giving every registered function the same name as the dispatcher, `def to_text(...)`. That
  replaces the dispatcher with the last registered function. Use `_`.
