## Hint 1

Write a helper that updates one prior given one result. Which two numbers change when the result is negative?

## Hint 2

```text
for r in results:
    if r:  num = sens * p;        den = num + fpr * (1 - p)
    else:  num = (1 - sens) * p;  den = num + (1 - fpr) * (1 - p)
    p = num / den
```
