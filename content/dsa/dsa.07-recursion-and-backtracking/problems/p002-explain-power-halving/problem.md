# Explain: power by repeated halving

Here are two ways to compute `x ** n` for a whole number `n >= 0`:

```python
def power(x, n):
    if n == 0:
        return 1
    return x * power(x, n - 1)


def fast_power(x, n):
    if n == 0:
        return 1
    half = fast_power(x, n // 2)
    if n % 2 == 0:
        return half * half
    return half * half * x
```

Answer in `answer.md`, in your own words (150 to 250 words):

1. `power(2, 10**6)` crashes. What error do you get, and why? Use the words *call stack*, *depth* and *recursion limit*.
2. How deep does `fast_power(2, 10**6)` go? Show the first few values of `n` along the chain of calls, and say how the depth grows with `n`.
3. Why does `fast_power` compute `half` **once** and multiply it by itself, instead of writing `fast_power(x, n // 2) * fast_power(x, n // 2)`? How many calls would that second version make?
4. Is raising the limit with `sys.setrecursionlimit(10**7)` a good fix for `power`? Give one reason.

Then compare with the model answer in `answer.md` and with `solution.md`, and rate yourself.
