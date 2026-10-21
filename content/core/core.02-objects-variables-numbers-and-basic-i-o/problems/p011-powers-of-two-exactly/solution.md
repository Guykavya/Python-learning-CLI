## Approach

Stay in the world of `int`. Python ints grow as large as memory allows, so `2 ** 1000`
is computed with all 302 digits.

## Code

```python
n = int(input())
p = 2 ** n
print(p)
print(p % 1000)
```

## Why `math.pow` is wrong here

`math.pow` always converts to `float`. A float has only 53 bits of precision, so
`2.0 ** 54` is still exact but `float(2 ** 100)` prints as `1.2676506002282294e+30`, and
`2.0 ** 1024` raises `OverflowError`.

## Another way

`pow(2, n)` (the built-in, not `math.pow`) also returns an exact int.
`pow(2, n, 1000)` computes the last three digits directly and is much faster for huge `n`.
