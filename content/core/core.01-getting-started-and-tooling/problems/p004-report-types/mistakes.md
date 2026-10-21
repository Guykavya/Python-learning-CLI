- Expecting `label` to be an `int`. The value `"42"` is text because of the quotes.
  This is the same reason `input()` always gives you a `str`.
- Writing `true` or `none` in lowercase: those are just undefined names and give a `NameError`.
- Printing the value instead of its type: `print(count)` shows `42`, not `<class 'int'>`.
