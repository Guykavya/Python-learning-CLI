# Evaluate an expression tree

Arithmetic expressions are stored as nested tuples:

- a number (`int` or `float`) is an expression;
- `(op, left, right)` with `op` one of `"+"`, `"-"`, `"*"`, `"/"` is an expression, where `left`
  and `right` are expressions;
- `("neg", x)` is an expression meaning minus `x`.

Write:

1. `evaluate(expr)` that returns the value (`"/"` is true division).
2. `to_text(expr)` that returns a fully parenthesised string: numbers as `str(n)`, binary
   operations as `(left op right)` with spaces, and negation as `-x`.

Use a **dispatch dict** from operator symbol to a two-argument function (lambdas are fine) for
the binary operators, instead of an `if`/`elif` chain on `op`.

**Examples**

```python
e = ("+", 2, ("*", 3, 4))
evaluate(e)                    # 14
to_text(e)                     # '(2 + (3 * 4))'
evaluate(("neg", ("-", 1, 5))) # 4
to_text(("neg", ("-", 1, 5)))  # '-(1 - 5)'
evaluate(("/", 7, 2))          # 3.5
evaluate(42)                   # 42
to_text(42)                    # '42'
```
