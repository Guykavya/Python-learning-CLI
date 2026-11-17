# Evaluate division

You are given equations `a / b = k` as two lists: `equations[i] = (a, b)` (variable names, strings) and `values[i] = k` (a positive float). Write `evaluate(equations, values, queries)`: for every query `(x, y)` in `queries`, the value of `x / y`, or `-1.0` if it cannot be worked out from the equations. Return a list of floats.

This is Example 2 of chapter section 18: the variables are vertices, `a / b = k` gives an edge `a -> b` with weight `k` and an edge `b -> a` with weight `1 / k`, and following a path **multiplies** the weights: `a / c = (a / b) * (b / c)`.

Rules:

- A variable that appears in no equation is unknown: any query with it gives `-1.0`, even `x / x`.
- For a known variable, `x / x` is `1.0`.
- Two variables in different groups (no path between them) give `-1.0`.
- The equations never contradict each other. Answers are compared with a relative tolerance of `1e-9`.

## Example

```python
>>> evaluate([("a", "b"), ("b", "c")], [2.0, 3.0],
...          [("a", "c"), ("c", "a"), ("b", "a"), ("a", "x"), ("x", "x"), ("a", "a")])
[6.0, 0.16666666666666666, 0.5, -1.0, -1.0, 1.0]
```

## Constraints

- `1 <= len(equations) <= 2000`, `1 <= len(queries) <= 2000`, values between `0.01` and `100`.

## Think about

Why does each equation need **two** edges? What must you remember while searching so that a cycle of equations does not make you walk forever?
