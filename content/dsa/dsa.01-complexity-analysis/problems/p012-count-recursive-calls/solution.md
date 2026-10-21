## Walkthrough

| n | fib(n) | C(n) = 1 + C(n-1) + C(n-2) |
|---|---|---|
| 0 | 0 | 1 |
| 1 | 1 | 1 |
| 2 | 1 | 3 |
| 3 | 2 | 5 |
| 4 | 3 | 9 |
| 5 | 5 | 15 |
| 6 | 8 | 25 |
| 7 | 13 | 41 |
| 8 | 21 | 67 |
| 9 | 34 | 109 |
| 10 | 55 | 177 |

Output:

```
0 0 1
1 1 1
2 1 3
3 2 5
4 3 9
5 5 15
10 55 177
```

## Key idea

Each call for `n >= 2` makes two more calls, and the same small values are recomputed again and again:
`fib(10)` computes `fib(2)` 34 times. The count obeys `C(n) = 1 + C(n-1) + C(n-2)`, which grows like the
Fibonacci numbers themselves, multiplying by about 1.6 every time `n` goes up by one. That is exponential time,
O(1.62^n), often loosely written O(2^n). `fib(40)` makes about 330 million calls, which takes minutes in Python.

A loop that keeps the last two values computes `fib(n)` in n steps. You will learn to make the recursive version
fast too (by remembering answers, called memoisation) in the dynamic programming module.

In fact `C(n) = 2 * fib(n + 1) - 1`: check it against the table.
