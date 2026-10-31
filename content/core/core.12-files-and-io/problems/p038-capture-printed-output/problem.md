# Capture what a function prints

Some functions `print` instead of returning a value. To test them (or to log them) you can send `sys.stdout` into
a `StringIO`, a file-like object that lives in memory. `contextlib.redirect_stdout` and `redirect_stderr` do it
and put the old stream back for you.

Write `capture_output(func, *args, **kwargs)` in `solution.py`:

- Call `func(*args, **kwargs)` while both **stdout** and **stderr** are redirected into two `StringIO` objects.
- Return a tuple `(result, out_text, err_text)`: the return value of `func`, and everything it printed to each stream.
- If `func` raises, the error goes up unchanged, and the streams must be back to normal.
- Nothing printed by `func` may reach the real screen.

**Example**

```python
def hello(name):
    print("hi", name)
    print("careful", file=sys.stderr)
    return 42

capture_output(hello, "Ana")   # (42, "hi Ana\n", "careful\n")
```
