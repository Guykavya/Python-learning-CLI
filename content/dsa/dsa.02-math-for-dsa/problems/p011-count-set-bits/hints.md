## Hint 1

Write 12 (`1100`) and 11 (`1011`) in binary, one under the other. Which bits change when you subtract 1 from 12?

## Hint 2

Subtracting 1 flips the lowest 1-bit to 0 and every 0-bit below it to 1. So `n & (n - 1)` is `n` with only its
lowest 1-bit removed. How many times can you do that before `n` is 0?

## Hint 3

```
count = 0
while n > 0:
    n = n & (n - 1)
    count += 1
print count
```
