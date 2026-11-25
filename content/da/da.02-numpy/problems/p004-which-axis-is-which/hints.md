## Hint 1

Write down the input shape and the shape you want. Which axis must disappear? For the stack `(n, h, w)` → `(n,)`, how many axes disappear?

## Hint 2

```text
column_means: (rows, cols) -> (cols,)   a.mean(axis=0)
row_maxes:    (rows, cols) -> (rows,)   a.max(axis=1)
per_image:    (n, h, w)    -> (n,)      stack.mean(axis=(1, 2))   # a tuple of axes
```
