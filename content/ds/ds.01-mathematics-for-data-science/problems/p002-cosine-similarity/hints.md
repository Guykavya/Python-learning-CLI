## Hint 1

Write down the three quantities you need: `x . y`, `|x|` and `|y|`. What happens to the division when one length is 0?

## Hint 2

```text
if length(x) == 0 or length(y) == 0: raise ValueError(...)
return (x . y) / (length(x) * length(y))
```
Use `np.dot` or `@` for the dot product.
