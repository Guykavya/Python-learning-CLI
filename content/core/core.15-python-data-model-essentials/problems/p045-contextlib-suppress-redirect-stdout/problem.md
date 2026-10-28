# `contextlib` helpers: `suppress` and `redirect_stdout`

The standard library has ready-made context managers for common jobs. In `solution.py` use them
(do not write your own classes):

- `contextlib.suppress(*exceptions)` ignores the listed exceptions inside the block.
- `contextlib.redirect_stdout(target)` and `redirect_stderr(target)` send everything `print` writes
  to `target` (any object with `write`, for example `io.StringIO()`) and restore the real streams
  when the block ends, even if it raised.

Write three functions:

- `capture(func, *args, **kwargs)`: calls `func(*args, **kwargs)` with both stdout and stderr
  captured, and returns the tuple `(result, stdout_text, stderr_text)`. Nothing reaches the real
  streams. Exceptions from `func` propagate (and the streams are restored).
- `remove_if_exists(path)`: deletes the file with `os.remove`. Returns `True` if it was deleted and
  `False` if there was no such file. Other errors are not hidden.
- `to_int_or(text, default=None)`: `int(text)`, or `default` if that raises `ValueError` or
  `TypeError`. No other exception is hidden.

**Example**

```python
def hello():
    print("hi")
    return 5

capture(hello)              # (5, 'hi\n', '')
remove_if_exists("gone")    # False
to_int_or("12")             # 12
to_int_or("twelve", -1)     # -1
```
