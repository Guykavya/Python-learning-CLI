## Hint 1

Draw the tree of `fib(5)`: which sub-trees are computed more than once? What if the second time you could just read the answer?

## Hint 2

Before computing `fib(n)`, check `if n in memo: return memo[n]`. After computing it, store `memo[n] = result`.

## Hint 3

```
memo = {}
def fib(n):
    if n < 2: return n
    if n in memo: return memo[n]
    memo[n] = fib(n - 1) + fib(n - 2)
    return memo[n]
```
