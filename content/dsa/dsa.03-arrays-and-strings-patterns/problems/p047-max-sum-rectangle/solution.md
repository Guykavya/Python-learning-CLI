## Approach

Every rectangle is "a band of rows" times "a stretch of columns". Fix the band (`top`, `bottom`): squashing each
column to its sum over the band turns the rectangle question into the maximum-subarray question on one row of
length `c`, which Kadane answers in O(c). There are `r (r + 1) / 2` bands, and moving `bottom` down one row updates
the column sums in O(c) instead of rebuilding them.

## Code

```python
r, c = [int(x) for x in input().split()]
grid = [[int(x) for x in input().split()] for _ in range(r)]

best = grid[0][0]
for top in range(r):
    col = [0] * c
    for bottom in range(top, r):
        row = grid[bottom]
        for j in range(c):
            col[j] += row[j]
        cur = col[0]
        if cur > best:
            best = cur
        for j in range(1, c):
            if cur < 0:
                cur = col[j]
            else:
                cur += col[j]
            if cur > best:
                best = cur
print(best)
```

For the example, the band of rows 2 to 4 squashes to `-9 4 15 10 -2`, and Kadane on that gives `4 + 15 + 10 = 29`.

## Complexity

O(r^2 c) time: `r (r + 1) / 2` bands, O(c) each. For 150 x 150 that is about 1.7 million steps, against about 130
million rectangles for the brute force. O(c) extra memory. If `r` is much bigger than `c`, transpose the grid first
so that the squared factor is the smaller side.

## Another way

Fix the left and right **columns** instead, squash each row, and find the best band of rows with prefix sums: the
best band ending at row `i` is `P[i] - min(P[0..i-1])`. It is the same idea turned 90 degrees, and Kadane and "prefix
minus smallest earlier prefix" are two faces of the same algorithm.
