## Approach

Group the `i` values by their step count. The steps for `i` are the number of doublings `1, 2, 4, ...` that stay
`<= i`, which is `floor(log2 i) + 1`, the number of binary digits of `i`. All numbers from `2^(k-1)` to `2^k - 1` take
exactly `k` steps. Walk over the groups, add `k` times the size of each group, and cut the last group at `n`.

For `n = 7`: group k = 1 is {1} (1 step each), k = 2 is {2, 3}, k = 3 is {4, 5, 6, 7}: `1*1 + 2*2 + 3*4 = 17`.

## Code

```python
n = int(input())
count = 0
k = 1
low = 1
while low <= n:
    high = min(n, 2 * low - 1)
    count += k * (high - low + 1)
    low = low * 2
    k += 1
print(count)
```

## Complexity

O(log n): one pass per group, and `low` doubles each pass, so there are about 60 passes for `n = 10^18`.
O(1) space. The starter is O(n log n).

## Another way

Count by columns instead of rows. The inner line runs once for every pair `(i, j)` with `j` a power of two and
`j <= i`. For a fixed power `j`, the values `i = j, j + 1, ..., n` all reach it: `n - j + 1` of them. So the count is the
sum of `n - j + 1` over all powers of two `j <= n`, which is also a loop of about 60 steps. Swapping the order of a
double sum like this is a powerful counting trick.

`i.bit_length()` gives the number of binary digits directly, but you still must not loop over all `i`.
