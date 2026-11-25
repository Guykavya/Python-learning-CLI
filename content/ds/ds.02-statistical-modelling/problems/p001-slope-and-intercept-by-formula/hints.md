## Hint 1

What does the bottom of the slope fraction become when all x are equal? What does Python (or NumPy) do with that division?

## Hint 2

```text
xm, ym = mean(x), mean(y)
sxx = sum((x - xm)^2)
if sxx == 0: raise ValueError
slope = sum((x - xm) * (y - ym)) / sxx
intercept = ym - slope * xm
```
