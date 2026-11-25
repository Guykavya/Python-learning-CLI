# Project a onto d

Chapter section 1.6. The **projection** of `a` onto the direction `d` is the shadow of `a` on the line through `d`: `((a . d) / (d . d)) * d`. What is left over, `a - p`, is perpendicular (orthogonal) to `d`.

Write `project(a, d)` returning the projection as a NumPy array. `d` need **not** have length 1. If `d` is the zero vector raise `ValueError`.

## Example

```text
project([3, 4], [1, 0])  ->  [3, 0]
project([2, 0], [0, 3])  ->  [0, 0]     (a is perpendicular to d)
project([1, 1], [2, 0])  ->  [1, 0]     (d has length 2)
```
