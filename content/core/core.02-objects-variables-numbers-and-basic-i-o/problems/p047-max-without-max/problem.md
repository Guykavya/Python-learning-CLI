# Larger and smaller without max()

Read three whole numbers `a`, `b`, `c` (any size, may be negative). Print three lines:

1. the larger of `a` and `b`
2. the smaller of `a` and `b`
3. the largest of all three

**Rules:** do not use `max()`, `min()` or `sorted()`. You have not learned `if`.
Find a formula with `abs()` instead.

**Example**

Input:
```
3
8
5
```
Output:
```
8
3
8
```

Idea: `a + b` is the sum of the larger and the smaller. `abs(a - b)` is the gap between them.
