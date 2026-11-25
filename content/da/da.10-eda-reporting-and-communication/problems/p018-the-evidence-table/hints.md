## Hint 1

Write a small function `verdict(r)` for one result and test it on the two examples by hand. Which condition must be checked first if an interval is both "above the null" and "within the margin"?

## Hint 2

```text
up: supported if lo > null; opposite if hi < null
down: supported if hi < null; opposite if lo > null
small = null - margin <= lo and hi <= null + margin
if supported: ... elif opposite or small: "not supported" else "inconclusive"
```
