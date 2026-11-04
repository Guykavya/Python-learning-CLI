## Approach

Two pointers start at the two ends, the widest container. At each step, the **shorter** wall is the problem:
every remaining container that keeps it is narrower and can be no taller than it, so it cannot do better than
the area just measured. So we drop the shorter wall and move that pointer inward. Each step removes one wall
from consideration for good, which is why `n - 1` steps are enough.

When the heights are equal, either pointer can move: any better container must be taller than both walls, so it
can use neither of them.

## Code

```python
n = int(input())
h = [int(x) for x in input().split()]

l, r = 0, n - 1
best = 0
while l < r:
    area = min(h[l], h[r]) * (r - l)
    if area > best:
        best = area
    if h[l] < h[r]:
        l += 1          # the shorter wall limits every container that keeps it: drop it
    else:
        r -= 1
print(best)
```

The first steps on the example (1-based positions):

| l | r | heights | area | best | move |
|---|---|---|---|---|---|
| 1 | 9 | 1, 7 | 1 * 8 = 8 | 8 | l (1 < 7) |
| 2 | 9 | 8, 7 | 7 * 7 = 49 | 49 | r (8 > 7) |
| 2 | 8 | 8, 3 | 3 * 6 = 18 | 49 | r |
| 2 | 7 | 8, 8 | 8 * 5 = 40 | 49 | r (equal) |

The remaining containers are narrower and none reaches 49.

## Complexity

O(n) time: every step moves one pointer, and they meet after `n - 1` steps. O(1) extra memory.

## Another way

Sort the walls from tallest to shortest. When you reach wall `i` with height `h[i]`, every wall seen so far is at
least as tall, so the best container with `i` as its shorter side reaches the farthest such wall: keep the
smallest and largest position seen so far. That is O(n log n), and it is a good way to check the two-pointer
answer.
