## Approach

Recipe: state `T(i)`, transition `T(i) = T(i-1) + T(i-2) + T(i-3)`, base `0, 1, 1`. A table would be `t[0..n]`, but each cell reads only the three cells before it, so we keep a window of three values and slide it (chapter section 6).

```python
def tribonacci(n):
    a, b, c = 0, 1, 1            # T(i), T(i+1), T(i+2) with i = 0
    for _ in range(n):
        a, b, c = b, c, a + b + c
    return a
```

After `k` steps, `a = T(k)`. After `n` steps, `a = T(n)`. For `n = 0` the loop does not run and `a = 0`. The tuple assignment evaluates `b, c, a + b + c` with the **old** values first, then assigns all three.

## Complexity

`O(n)` additions and `O(1)` variables. (Strictly, the numbers themselves grow to about `0.88 n` bits, so each addition costs `O(n)` bit operations; that is the same for any method.)

## Another way

The full table, then shrink it:

```python
def tribonacci(n):
    t = [0, 1, 1] + [0] * n
    for i in range(3, n + 1):
        t[i] = t[i - 1] + t[i - 2] + t[i - 3]
    return t[n]
```

Same time, `O(n)` cells. This is the "write the table first, then roll it" workflow of chapter section 6. It breaks the memory rule of this problem, so use it only as a checker.
