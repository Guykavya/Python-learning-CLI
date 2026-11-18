## Hint 1

The naive version is the definition written as code: two base cases (`n < 2` returns `n`) and one recursive line. The memo version is the **same function** with a notebook: before working, look in the notebook; after working, write the answer in it. Which Python decorator from chapter section 3 does that for you?

## Hint 2

The table version follows the conversion recipe of chapter section 4: the memo becomes a list of size `n + 1`, the base cases become the first assignments, and the recursive calls become list reads. Careful with `n = 0`: a list of size 1 has no index 1.

## Hint 3

```
fib_naive(n):  if n < 2: return n
               return fib_naive(n-1) + fib_naive(n-2)

fib_memo(n):   same body, decorated with @functools.cache
               (or: if n in memo: return memo[n]; ...; memo[n] = result)

fib_table(n):  f = [0] * (n + 1)
               if n >= 1: f[1] = 1
               for i in 2..n: f[i] = f[i-1] + f[i-2]
               return f[n]
```
