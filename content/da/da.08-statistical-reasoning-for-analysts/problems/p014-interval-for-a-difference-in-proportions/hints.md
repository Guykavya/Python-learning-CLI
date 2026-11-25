## Hint 1

What are `p1` and `p2`? What goes under the square root, and which constant multiplies the standard error?

## Hint 2

```text
p1 = k1 / n1 ; p2 = k2 / n2 ; d = p1 - p2
se = sqrt(p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2)
return d, (d - z * se, d + z * se)
```
