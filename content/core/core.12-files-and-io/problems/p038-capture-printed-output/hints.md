## Hint 1

`redirect_stdout(target)` is a context manager. Which two objects do you need to create first, and can one
`with` statement hold two context managers? What is the method of `StringIO` that gives you the collected text?

## Hint 2

```
out = io.StringIO()
err = io.StringIO()
with redirect_stdout(out), redirect_stderr(err):
    result = func(*args, **kwargs)
return result, out.getvalue(), err.getvalue()
```
