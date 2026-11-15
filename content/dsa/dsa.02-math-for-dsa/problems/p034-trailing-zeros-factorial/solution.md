## Approach

Each multiple of `p` in `1..n` contributes at least one factor `p`: there are `n // p` of them. Each multiple of `p^2` contributes
one more (there are `n // p^2`), and so on. Summing gives the exponent. Since `n // p^2 = (n // p) // p`, we can repeat
`n = n // p` and add each time until `n` is 0.

## Code

```python
q = int(input())
for _ in range(q):
    n, p = [int(x) for x in input().split()]
    total = 0
    while n > 0:
        n //= p
        total += n
    print(total)
```

## Complexity

O(log_p n) per query: about 60 steps for `p = 2` and `n = 10^18`, one step for large `p`. Looping over `1..n` is O(n).

## Another way

`(n - s) / (p - 1)`, where `s` is the sum of the digits of `n` written in base `p`. For `n = 10`, `p = 2`: `10 = 1010` in
binary, `s = 2`, `(10 - 2) / 1 = 8`. It gives the same number, and shows why the sum is always an integer.
