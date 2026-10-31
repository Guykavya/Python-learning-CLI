# functools.wraps keeps the name and docstring

The decorator in `starter.py` works: it strips spaces from a function's text result. But it hides the
original function. After decoration, `__name__` is `'wrapper'` and the docstring is gone. Tools that use
these (`help()`, logs, test reports, registries) then show the wrong thing.

Change `strip_result(func)` so that the decorated function keeps the original's metadata.
Use `functools.wraps`.

After your change:

- `f.__name__` is the original name,
- `f.__doc__` is the original docstring,
- `f.__wrapped__` is the original function (`wraps` sets this for you),
- the result is still stripped, and arguments still pass through.

**Example**

```python
@strip_result
def read_name(raw):
    """Return the part after the colon."""
    return raw.split(":")[1]

read_name("id: Ann  ")    # 'Ann'
read_name.__name__        # 'read_name'   (not 'wrapper')
read_name.__doc__         # 'Return the part after the colon.'
```
