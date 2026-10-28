# A callable object that counts its calls

A function cannot remember anything between calls, but an **object with `__call__`** can. Write
`CallCounter` in `solution.py`:

- `CallCounter(func)` wraps any callable.
- Calling the object (`c(1, 2, x=3)`) calls `func` with the same arguments, **returns its result**,
  and adds one to the attribute `count`. The call is counted even if `func` raises (the exception
  propagates).
- `count` starts at `0`; `reset()` sets it back to `0`.
- It also works as a decorator: `@CallCounter` above a function.

**Example**

```python
@CallCounter
def greet(name):
    return "hi " + name

greet("Asha")     # 'hi Asha'
greet("Ravi")     # 'hi Ravi'
greet.count       # 2
callable(greet)   # True
greet.reset()
greet.count       # 0
```
