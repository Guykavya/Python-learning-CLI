## Approach

Turn "find a pair" into "for each element, look up its partner". Scan positions from left to right. At position
`j`, the partner value is `need = t - a[j]`. If `need` is in a dict of earlier values, we have a pair. Otherwise
record `a[j]`. Because we scan `j` in increasing order and stop at the first success, `j` is the smallest possible;
because the dict keeps the first position of each value, `i` is the smallest for that `j`.

## Code

```python
n, t = [int(x) for x in input().split()]
a = [int(x) for x in input().split()]

first_pos = {}
answer = "none"
for j in range(n):
    need = t - a[j]
    if need in first_pos:
        answer = f"{first_pos[need] + 1} {j + 1}"
        break
    if a[j] not in first_pos:
        first_pos[a[j]] = j
print(answer)
```

## Complexity

- Time: O(n) on average, one dict lookup and at most one insert per position. The starter is O(n^2).
- Space: O(n) for the dict.

On this machine the reference needs about 0.2 seconds for 200000 numbers; the starter needs about 2 * 10^10
additions in the worst case, which is many minutes.

## Another way

Sort the values together with their positions, then use two pointers, one at each end: if the sum is too small,
move the left pointer right; if too big, move the right pointer left. That is O(n log n) and needs care to
respect this problem's tie rule (you would collect all pairs and pick the best), so the dict is simpler here.
You will meet two pointers properly in dsa.03.
