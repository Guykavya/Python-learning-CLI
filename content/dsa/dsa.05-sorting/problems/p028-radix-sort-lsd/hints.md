## Hint 1

Suppose you sort by the tens digit **last**. Two numbers with the same tens digit: how do you want them ordered? What did the previous pass already do for them?

## Hint 2

Because each pass is stable, numbers equal in the current digit keep the order from the previous (less significant) digits. That is why you go from the **least** significant digit to the most significant.

## Hint 3

```
exp = 1
while max(a) // exp > 0:
    buckets = [[] for _ in range(10)]
    for x in a: buckets[(x // exp) % 10].append(x)
    a = [x for b in buckets for x in b]
    exp *= 10
```
