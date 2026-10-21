## Hint 1

How do you test whether one number is divisible by another using `%`? And which numbers does `range(a, b)` give: does it include `b`?

## Hint 2

Visit every number from `a` to `b`, including `b`, and add 1 to a counter whenever the number leaves remainder 0 when divided by `k`.

## Hint 3

```
read a, b, k
count = 0
for x from a to b inclusive  (range(a, b + 1)):
    if x % k == 0:
        count = count + 1
print count
```
