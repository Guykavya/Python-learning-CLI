# Fix the broken min stack

`starter.py` holds a `MinStack` that uses **two** lists to save memory: `items` holds everything, and `mins` holds only the values that were a new minimum when they arrived. `get_min()` is `mins[-1]`. All operations are `O(1)`.

A user reports:

```python
>>> m = MinStack()
>>> m.push(5); m.push(3); m.push(3)
>>> m.pop()
3
>>> m.get_min()          # the stack is [5, 3], so this should be 3
5
```

and with `push(2); push(2); pop(); pop()` followed by `push(9)` and `get_min()`, it even crashes with `IndexError`.

1. Find the bug by tracing `items` and `mins` for the report above.
2. Fix it with the **smallest** change. Keep the two-list design: `mins` must still grow only when a value arrives that is **not larger** than the current minimum (the tests push 1,000 increasing values and check that `mins` stays short).
3. Do not change the method names or what they return.

## Example

After the fix:

```python
>>> m = MinStack()
>>> m.push(5); m.push(3); m.push(3)
>>> m.pop(), m.get_min()
(3, 3)
>>> m.pop(), m.get_min()
(3, 5)
```

## Think about

`mins` stores each minimum **once**. How many copies of `3` were pushed, and how many times will `pop` take a `3` away from `mins`?
