## Approach

`water[i] = min(max(h[0..i]), max(h[i..n-1])) - h[i]`. Recomputing both maxima for every bar is O(n^2). Two O(n) ways:

1. **Prefix and suffix maxima.** One pass left to right builds `left_max[i]`, one pass right to left builds
   `right_max[i]`, a third pass sums. O(n) time, O(n) memory.
2. **Two pointers.** Keep `left_max` (highest bar in `h[0..i-1]`) and `right_max` (highest in `h[j+1..n-1]`). If
   `left_max <= right_max`, bar `i`'s level is `max(left_max, h[i])`: its true right maximum is at least `right_max`,
   which is already at least `left_max`, so the left side is the limit. Settle bar `i` and move on. Otherwise settle
   bar `j` from the right. O(1) extra memory.

## Code

```python
n = int(input())
h = [int(x) for x in input().split()]

i, j = 0, n - 1
left_max = right_max = 0
total = 0
while i <= j:
    if left_max <= right_max:
        left_max = max(left_max, h[i])
        total += left_max - h[i]
        i += 1
    else:
        right_max = max(right_max, h[j])
        total += right_max - h[j]
        j -= 1
print(total)
```

For `n = 0`, `j = -1` and the loop never runs: the answer is 0 without a special case.

## Complexity

O(n) time: every pass of the loop settles one bar. O(1) extra memory (besides the input list).

## Another way

```python
left = h[:]                       # running maximum from the left
for i in range(1, n):
    left[i] = max(left[i - 1], h[i])
right = h[:]                      # running maximum from the right
for i in range(n - 2, -1, -1):
    right[i] = max(right[i + 1], h[i])
print(sum(min(left[i], right[i]) - h[i] for i in range(n)))
```

This is the prefix-sum idea with `max` instead of `+`: a running "best so far" in each direction. It is easier
to get right first; the two-pointer version is the same reasoning with the arrays thrown away.
