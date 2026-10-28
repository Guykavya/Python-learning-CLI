## Hint 1

A `with` can contain several managers separated by commas: `with redirect_stdout(a), redirect_stderr(b):`. What do you need to collect the text, and which method of it gives the whole text afterwards?

## Hint 2

`io.StringIO()` is an in-memory text file; `.getvalue()` returns everything written. For `remove_if_exists`, `return True` after `os.remove(path)` can sit **inside** `with suppress(FileNotFoundError):`: if `remove` raises, the `return` is skipped and execution continues after the `with`, where you return `False`.

## Hint 3

```
capture: out, err = StringIO(), StringIO()
         with redirect_stdout(out), redirect_stderr(err): result = func(*args, **kwargs)
         return result, out.getvalue(), err.getvalue()
remove_if_exists: with suppress(FileNotFoundError): os.remove(path); return True
                  return False
to_int_or: with suppress(ValueError, TypeError): return int(text)
           return default
```
