- **Restoring with `sys.settrace(None)`.** That switches off whatever was there before: the
  debugger you were using, or coverage measurement for the rest of the test run.
- **No `try/finally`.** If `fn` raises, your tracer stays installed and slows down (and counts)
  everything that runs afterwards.
- **Local tracer returning `None`.** After the first line it stops receiving events, so every
  line shows 1 or is missing.
- **Absolute line numbers.** `frame.f_lineno` is the line in the file; subtract
  `co_firstlineno` and add 1.
- **Comparing by name (`frame.f_code.co_name == fn.__name__`).** Another function with the same
  name, or a nested `<genexpr>`, would be counted too. Compare the code object with `is`.
- **Tracing every frame.** Returning the local tracer for all frames counts the lines of called
  functions under the wrong numbers, and makes everything much slower.
- **Expecting a `for` line to run once per item.** It runs once more, for the check that ends
  the loop.
