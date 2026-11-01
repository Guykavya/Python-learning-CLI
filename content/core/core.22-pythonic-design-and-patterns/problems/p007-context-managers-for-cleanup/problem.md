# Context managers for cleanup

If you open something, you must close it, even when the code in between fails. The old way is
`try/finally`. The Python way is `with`: the object (or helper) promises to clean up, and you
cannot forget.

```python
with open_resource(name) as r:        # closed when the block ends, error or not
    return r.read()

with lock:                            # acquire on entry, release on exit
    ...

@contextmanager                        # write your own cleanup in 6 lines
def temp_setting(obj, name, value):
    ...
    try:
        yield
    finally:
        ...                            # runs on normal exit AND on an exception
```

`starter.py` does cleanup by hand with `try/finally` everywhere, and `temp_setting` does not exist
yet. Copy it to `solution.py` and:

1. Rewrite `read_all`, `copy_text` (two resources in **one** `with`) and `run_locked` with `with`.
2. Write `temp_setting(obj, name, value)`: it sets `obj.<name>` to `value` for the duration of a
   `with` block, then puts the **old value back**, also when the block raises (the exception still
   reaches the caller). If the attribute did not exist before, remove it afterwards. Use
   `@contextmanager` or a class; both are fine.
3. Rewrite `format_with_precision` using your `temp_setting`.

The tests use fake resources and locks that count how many times they were closed and released.
They are also checked with `ast`: the four functions above must use `with` and contain no
`try`.

**Example**

```python
class Cfg:
    precision = 6
    def fmt(self, n): return f"{n:.{self.precision}f}"

cfg = Cfg()
format_with_precision(cfg, [3.14159], 2)   # ['3.14']
cfg.precision                              # 6  (restored)
```
