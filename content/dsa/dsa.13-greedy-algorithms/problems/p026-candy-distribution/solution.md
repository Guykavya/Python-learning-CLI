## Approach

Two passes, each one greedy:

- **Left to right:** give each child 1, or one more than the left neighbour if its rating is higher. After this pass every "left" rule holds, with the fewest candies possible for those rules alone.
- **Right to left:** if a child's rating is higher than its right neighbour, raise it to at least `right neighbour + 1`. Raising never breaks a left rule (a child with more candies still beats a lower-rated left neighbour), and the left neighbour of a raised child is handled next in the same sweep.

Each child ends with `max(left[i], right[i])`, where `left[i]` and `right[i]` are the lengths of the strictly rising runs that end at `i` from each side. Both are **lower bounds** (a rising run of length `k` that ends at `i` forces at least `k` candies on `i`), and together they satisfy every rule, so the total is the minimum.

```python
def min_candies(ratings):
    n = len(ratings)
    c = [1] * n
    for i in range(1, n):
        if ratings[i] > ratings[i - 1]:
            c[i] = c[i - 1] + 1
    for i in range(n - 2, -1, -1):
        if ratings[i] > ratings[i + 1]:
            c[i] = max(c[i], c[i + 1] + 1)
    return sum(c)
```

Trace `[1, 3, 4, 5, 2]`: after the left pass `[1, 2, 3, 4, 1]`. Right pass: `i = 3`: 5 > 2, `max(4, 2) = 4`. `i = 2`: 4 < 5, unchanged, and so on. Total 11.

## Complexity

Two passes: `O(n)` time, `O(n)` space.

## Another way

Keep fixing broken rules until none is left: start with all ones; repeatedly scan, and whenever a child with a higher rating than a neighbour does not have more candies, set it to `neighbour + 1`. Values only ever go up, and each one stops at the smallest value that its rules force, so it ends at the same answer. It can take up to `n` sweeps (`O(n^2)`), which is why the two-pass greedy is better; it is a good brute-force check for small inputs.
