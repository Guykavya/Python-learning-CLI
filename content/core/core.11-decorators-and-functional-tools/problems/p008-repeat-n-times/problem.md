# @repeat(n): a decorator with an argument

`@repeat(3)` has brackets, so `repeat(3)` is **called first**. Its result must be a decorator, which is then
applied to the function. This needs three levels of functions: factory → decorator → wrapper.

Write `repeat(n)` in `solution.py`:

- `repeat(n)` returns a decorator.
- The decorated function, when called, calls the original `n` times with the same arguments and returns a
  **list** of the `n` results, in order.
- If `n` is less than 1, `repeat(n)` raises `ValueError` straight away (at decoration time, not at call time).
- Keep the original's `__name__` and `__doc__` with `functools.wraps`.

**Examples**

```python
@repeat(3)
def roll(sides=6):
    """Pretend dice roll."""
    return sides

roll()            # [6, 6, 6]
roll(sides=20)    # [20, 20, 20]
roll.__name__     # 'roll'

repeat(0)         # ValueError: n must be at least 1, got 0
```
