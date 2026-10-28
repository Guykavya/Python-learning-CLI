# Functions as values: apply_twice and compose

In Python a function is a value, like a number or a string. You can pass it to another function,
and you can return it from a function. Every decorator is built on these two facts.

Write two functions in `solution.py`:

1. `apply_twice(f, x)` calls `f` on `x`, then calls `f` again on that result, and returns the final value.
2. `compose(f, g)` does **not** call anything yet. It **returns a new function**. When you call that new
   function with `x`, it returns `f(g(x))`: first `g`, then `f`.

**Examples**

```python
def add_one(n):
    return n + 1

def double(n):
    return n * 2

apply_twice(add_one, 5)       # 7
apply_twice(double, 3)        # 12

h = compose(add_one, double)  # h(x) is add_one(double(x))
h(5)                          # 11
compose(double, add_one)(5)   # 12   (order matters)
compose(str.upper, str.strip)("  hi ")   # 'HI'
```
