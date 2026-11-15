## Hint 1

If `d` divides both `a` and `b`, does `d` also divide `a % b`? Write `a % b` as `a - k * b` to see.

## Hint 2

So `gcd(a, b) = gcd(b, a % b)`. Each step makes the numbers smaller. When does it stop? What is `gcd(a, 0)`?

## Hint 3

```
while b != 0:
    a, b = b, a % b
answer = a
```
