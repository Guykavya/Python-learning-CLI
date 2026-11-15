## Approach

`answer[i] = (a[0] * ... * a[i-1]) * (a[i+1] * ... * a[n-1])`: a **prefix product** times a **suffix product**,
the multiplication version of prefix sums. The first pass stores the prefix products in the answer list; the second
pass walks backwards with a running suffix product and multiplies it in. No division is needed, so zeros cause no
trouble: a zero simply makes every product that contains it 0.

Reducing modulo `10^9 + 7` after every multiplication keeps each number below about `10^18`, so every step is fast.
Python's `%` returns a value in `0 .. MOD-1` even for negative numbers, which is exactly the required output form.

## Code

```python
MOD = 10**9 + 7

n = int(input())
a = [int(x) for x in input().split()]

ans = [1] * n
left = 1                       # product of a[0..i-1]
for i in range(n):
    ans[i] = left
    left = left * a[i] % MOD

right = 1                      # product of a[i+1..n-1]
for i in range(n - 1, -1, -1):
    ans[i] = ans[i] * right % MOD
    right = right * a[i] % MOD

print(" ".join(map(str, ans)))
```

For `1 2 3 4`: after the first pass `ans = 1 1 2 6` (left products). The second pass multiplies by the right
products `24 12 4 1`: `24 12 8 6`.

## Complexity

O(n) time (two passes) and O(1) extra memory besides the answer list. Multiplying the other `n - 1` numbers for every
position is O(n^2).

## Another way

Division, done carefully. Count the zeros. With two or more zeros, every answer is 0. With exactly one zero, only
that position gets the product of the others; all the rest are 0. With no zeros, `answer[i] = total * inverse(a[i])`,
where the inverse modulo the prime `10^9 + 7` is `pow(a[i], MOD - 2, MOD)` (Fermat, from dsa.02). That works but
needs three cases and an O(log MOD) inverse per element; the prefix/suffix method needs none of that.
