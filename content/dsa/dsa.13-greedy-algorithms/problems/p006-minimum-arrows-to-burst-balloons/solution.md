## Approach

Sort the balloons by end. The balloon that ends first must be hit, and the best place to hit it is its **end**: every other balloon ends at or after that point, so shooting further right cannot miss one that a shot further left would hit. Shoot there, skip every balloon that this arrow also hits (start `<= shot_at`), and repeat with the next balloon that was missed (chapter section 5).

```python
def min_arrows(balloons):
    arrows = 0
    shot_at = float("-inf")
    for s, e in sorted(balloons, key=lambda b: b[1]):
        if s > shot_at:               # not hit by the last arrow (touching IS hit)
            arrows += 1
            shot_at = e               # shoot as far right as this balloon allows
    return arrows
```

The only difference from activity selection is the comparison. Balloons are closed, so a balloon starting exactly at `shot_at` is hit: the condition for a **new** arrow is `s > shot_at`, not `s >= last_end`.

## Complexity

`O(n log n)` for the sort, `O(n)` for the sweep, `O(n)` space for the sorted copy.

## Another way

Count groups: the answer is also the largest number of balloons no two of which share a point (a lower bound: each needs its own arrow), and the sweep reaches it. Or sort by start and keep the **smallest end** of the current group (`group_end = min(group_end, e)`); start a new group when a balloon starts after `group_end`.
