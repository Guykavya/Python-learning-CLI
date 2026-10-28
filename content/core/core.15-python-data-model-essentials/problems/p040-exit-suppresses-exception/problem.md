# Context managers that swallow or expect exceptions

`__exit__(exc_type, exc, tb)` receives the exception that ended the block (or `None, None, None` if
there was none). Its **return value** decides what happens next: a true value **swallows** the
exception (the program continues after the `with`), a false value lets it continue. Write two
classes in `solution.py`.

**`Ignore(*exc_types)`**

- `with Ignore(KeyError, ValueError) as ig: ...` swallows exceptions that are instances of the listed
  classes **or their subclasses**. Other exceptions propagate.
- `ig.exception` is the swallowed exception object, or `None`. `ig.caught` (a property) is `True`
  if something was swallowed. Each new `with` starts clean (`exception = None`).

**`Expect(exc_type)`**: the opposite, like a tiny test helper.

- The block **must** raise `exc_type` (or a subclass): that exception is swallowed and stored in
  `.exception`.
- If the block finishes without any exception, raise `AssertionError` with a message that contains the
  name of the expected class.
- If the block raises a different exception, let it propagate.

**Example**

```python
with Ignore(FileNotFoundError) as ig:
    open("no-such-file.txt")
    print("never printed")
print(ig.caught)               # True

with Expect(ZeroDivisionError) as ex:
    1 / 0
print(type(ex.exception).__name__)     # ZeroDivisionError

with Expect(ValueError):
    pass                       # AssertionError: expected ValueError, but nothing was raised
```
