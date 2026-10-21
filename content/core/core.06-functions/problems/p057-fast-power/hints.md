## Hint 1

How many times can you halve 100,000 before reaching 0? That is roughly how deep the recursion goes.

## Hint 2

Calling `power(base, exp // 2)` twice (once for each factor) gives the right answer but makes as many calls as the slow version. Store it in a variable.

## Hint 3

```
if exp == 0: return 1
half = power(base, exp // 2)
if exp % 2 == 0: return half * half
return half * half * base
```
