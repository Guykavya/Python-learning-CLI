- Expecting no output at all. That only happens for a `SyntaxError`. This is a
  run-time error, so lines 3 and 4 already printed.
- Thinking `print("Marks:", marks)` fails too. `print` accepts any values and
  converts them; only `+` between `str` and `int` fails.
- Writing `line 6` because that is where `message` is used. The error happens
  where the `+` runs.
- Swapping `str` and `int` in the message. The left side (`"Total: "`) is a
  `str`, so Python says it can only add another `str` to it.
