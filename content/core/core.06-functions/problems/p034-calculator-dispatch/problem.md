# Calculator with a dispatch table

Build a tiny calculator **without an `if`/`elif` chain on the operator**.

1. Write four functions `add(a, b)`, `subtract(a, b)`, `multiply(a, b)` and `divide(a, b)`.
   `divide` returns `None` when `b` is 0.
2. Create a module-level dict `OPERATIONS` mapping the symbols `"+"`, `"-"`, `"*"`, `"/"` to
   those functions (the functions themselves, not results of calling them).
3. Write `calculate(a, op, b)` that looks up `op` in `OPERATIONS` and calls the function. For an
   unknown operator it returns `None`.

**Examples**

```python
calculate(6, "+", 3)    # 9
calculate(6, "-", 3)    # 3
calculate(6, "*", 3)    # 18
calculate(6, "/", 3)    # 2.0
calculate(6, "/", 0)    # None
calculate(6, "%", 3)    # None
OPERATIONS["*"](4, 5)   # 20
```

Adding a new operator later should need only a new function and one new dict entry.
