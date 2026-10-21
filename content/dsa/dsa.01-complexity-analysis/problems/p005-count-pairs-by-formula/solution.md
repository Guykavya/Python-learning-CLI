## Approach

Count, do not simulate. For each `i`, the inner loop runs over `i + 1, ..., n - 1`, which is `n - 1 - i`
values. Adding over `i = 0 .. n - 1` gives `(n - 1) + (n - 2) + ... + 0`, the sum of the first `n - 1` whole
numbers, which is `n(n - 1) / 2`. This is also "the number of ways to choose 2 things out of n", because each
pair `i < j` is counted exactly once.

## Code

```python
n = int(input())
print(n * (n - 1) // 2)
```

## Complexity

O(1) time and space: one multiplication and one division, whatever `n` is. (For very large `n`, multiplying
big integers costs a little more, but for 19-digit numbers that is nothing.) The starter was O(n^2).

## Another way

Count pairs from the other side: each of the `n` values of `i` pairs with `n - 1` others, giving `n(n - 1)`
ordered pairs `(i, j)` with `i != j`. Each unordered pair appears twice (`(i, j)` and `(j, i)`), so divide by 2.

## Edge cases

- `n = 0` and `n = 1`: the formula gives 0, which is right, because there are no pairs.
- `n = 10^18`: Python integers have no size limit, but `/` produces a float, which keeps only about 16
  significant digits. Always use `//` when the exact answer is an integer.
