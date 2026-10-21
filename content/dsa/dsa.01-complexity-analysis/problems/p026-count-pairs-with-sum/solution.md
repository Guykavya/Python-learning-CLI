## Approach

Constraints first: `n = 2 * 10^5` rules out O(n^2), so aim for O(n) or O(n log n). Then a counting idea: each pair
`i < j` is decided at its right end `j`. At position `j`, the partners are the earlier positions holding `t - a[j]`.
If a dict remembers how many times each value has appeared so far, we can add that number in O(1). This counts
every pair exactly once (at its right end), and never pairs a position with itself because `a[j]` is added after
the lookup.

For `2 2 2 2` with `t = 4`: the counts added are 0, 1, 2, 3, total 6.

## Code

```python
n, t = [int(x) for x in input().split()]
a = [int(x) for x in input().split()]

count_so_far = {}
pairs = 0
for x in a:
    pairs += count_so_far.get(t - x, 0)
    count_so_far[x] = count_so_far.get(x, 0) + 1
print(pairs)
```

## Complexity

O(n) time on average and O(d) space for `d` different values. About 0.1 seconds for 200000 numbers here.

## Another way

Count all values first (`Counter`-style dict), then for each different value `v` with partner `w = t - v`:
if `v < w`, add `count[v] * count[w]`; if `v == w`, add `count[v] * (count[v] - 1) // 2`. Also O(n), and it shows the
counting formula from "Count the pairs without looping" again.

Or sort and use two pointers from both ends, handling runs of equal values carefully: O(n log n).
