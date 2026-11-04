## Hint 1

What is `5 ^ 5`? What is `5 ^ 0`? What is `a ^ b ^ a`? Does the order in which you XOR matter?

## Hint 2

If you XOR the whole list, every pair `x, x` turns into 0 no matter where the two copies sit. What remains?

## Hint 3

```
ans = 0
for each x in a:
    ans = ans ^ x
print(ans)
```
