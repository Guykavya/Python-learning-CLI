## Hint 1

How many sequences of `n` flips have exactly `k` heads? How many sequences are there in total?

## Hint 2

```text
if k < 0 or k > n: return 0.0
return comb(n, k) / 2**n
```
