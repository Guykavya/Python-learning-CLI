## Hint 1

This is like summing 1 to n, but with multiplication. What must the running value start at so that the first multiplication does not change it?

## Hint 2

Start `product` at 1 (starting at 0 makes everything 0). Multiply by each number from 1 to `n`. For `n = 0` the loop does not run, and 1 is the correct answer.

## Hint 3

```
product = 1
for i in range(1, n + 1):
    product = product * i
print product
```

Do not use `/` anywhere. Floats cannot hold 615 exact digits.
