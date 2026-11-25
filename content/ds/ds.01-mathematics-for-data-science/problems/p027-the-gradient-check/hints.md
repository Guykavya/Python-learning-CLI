## Hint 1

For coordinate `i`, which point is `p + h e_i` and which is `p - h e_i`? Fill the numerical gradient one entry at a time.

## Hint 2

```text
num[i] = (f(p + h e_i) - f(p - h e_i)) / (2 h)
return norm(a - num) / max(norm(a) + norm(num), 1e-12)
```
