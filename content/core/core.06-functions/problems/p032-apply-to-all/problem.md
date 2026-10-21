# Apply a function to every item

Write `apply_to_all(func, items)` that returns a **new list** with `func` applied to each item,
in order. The input list must not change.

Write it with a `for` loop; do not use `map` (you are building your own version of it).

**Examples**

```python
apply_to_all(len, ["a", "bcd", ""])      # [1, 3, 0]
apply_to_all(str.title, ["asha", "ravi"])   # ['Asha', 'Ravi']
apply_to_all(lambda n: n * n, [1, 2, 3]) # [1, 4, 9]
apply_to_all(abs, [])                    # []
```
