## Approach

The interval DP of section 17. Every bracketing of `A_i ... A_j` (with at least two matrices) ends with one multiplication that splits it at some `k`: left part `i..k`, right part `k+1..j`. The two parts are independent, so each must be bracketed optimally on its own.

- State: `f(i, j)` = cheapest cost for matrices `i..j`.
- Transition: `f(i, j) = min over k of f(i, k) + f(k+1, j) + dims[i] * dims[k+1] * dims[j+1]`.
- Base: `f(i, i) = 0`. Answer: `f(0, n-1)`.
- Order: by the length of the range, so both parts (shorter) are ready.

```python
def matrix_chain_cost(dims):
    n = len(dims) - 1                       # number of matrices
    f = [[0] * n for _ in range(n)]
    for length in range(2, n + 1):          # short ranges first
        for i in range(n - length + 1):
            j = i + length - 1
            f[i][j] = min(f[i][k] + f[k + 1][j] + dims[i] * dims[k + 1] * dims[j + 1]
                          for k in range(i, j))
    return f[0][n - 1]
```

For `[10, 30, 5, 60]`: `f[0][1] = 10*30*5 = 1500`, `f[1][2] = 30*5*60 = 9000`, and `f[0][2] = min(0 + 9000 + 10*30*60, 1500 + 0 + 10*5*60) = min(27000, 4500) = 4500`.

## Complexity

`O(n^2)` states, `O(n)` split points each: `O(n^3)` time, `O(n^2)` memory. For 150 matrices that is about 560,000 inner steps.

## Another way

Top-down, which finds the order by itself (section 17, "Order of evaluation, again"):

```python
import functools

def matrix_chain_cost(dims):
    @functools.cache
    def best(i, j):
        if i == j:
            return 0
        return min(best(i, k) + best(k + 1, j) + dims[i] * dims[k + 1] * dims[j + 1]
                   for k in range(i, j))
    return best(0, len(dims) - 2)
```

Without `@functools.cache` it is exactly the "try every bracketing" brute force: the count of bracketings is the Catalan number, which grows like `4^n`.
