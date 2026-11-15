## Hint 1

What is the base case in the rule above? What does the recursive call do with the two numbers?

## Hint 2

Check `gcd(12, 18)` by hand: `gcd(18, 12)`, `gcd(12, 6)`, `gcd(6, 0)`. Notice that the first call swaps the numbers by itself.

## Hint 3

```
def gcd(a, b):
    if b == 0: return a
    return gcd(b, a % b)
```
