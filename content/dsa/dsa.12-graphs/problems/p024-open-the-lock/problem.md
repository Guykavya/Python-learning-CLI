# Open the lock

A combination lock has `k` wheels, each showing a digit `0 .. 9`. One **move** turns one wheel one step up or down; the wheels wrap around (`9` up is `0`, `0` down is `9`). The lock starts at all zeros, `"0" * k`. Some combinations are **dead ends**: if the lock ever shows one of them, it jams, so you may never pass through them.

This is a BFS on a **state graph** (chapter section 3, "BFS on a state graph"): the states are the `10**k` combinations and the moves are the edges. The chapter solves the 4-wheel lock; here the number of wheels is `k = len(target)`.

Write `open_lock(deadends, target)`. It returns the fewest moves from `"0" * k` to `target`, or `-1` if it is impossible.

Rules:

- `1 <= k <= 6`; every string in `deadends` has length `k`.
- If the start `"0" * k` is a dead end, the answer is `-1`, even when `target` is the start.
- If `target` is a dead end, the answer is `-1`.
- If `target` is the start (and the start is not dead), the answer is `0`.

## Example

```python
>>> open_lock(["0201", "0101", "0102", "1212", "2002"], "0202")
6
>>> open_lock(["8888"], "0009")
1
>>> open_lock(["9", "1"], "5")
-1
>>> open_lock([], "55")
10
```

In the third example the single wheel cannot leave `0`: both neighbours `1` and `9` are dead. In the last one each wheel needs 5 moves.

## Constraints

`0 <= len(deadends) <= 10**4`. `O(10**k * k)` time: at most a million states for `k = 6`.
