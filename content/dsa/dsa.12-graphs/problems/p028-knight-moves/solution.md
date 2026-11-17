## Approach

The board is a graph that we never build: the vertices are the `n * n` squares, and each square has up to 8 edges, the legal knight moves. Every move costs one step, so the shortest number of moves is a BFS distance (chapter section 3). We generate the neighbours of a square when we pop it, keep only those on the board, and mark them as seen when we push them.

```python
from collections import deque

MOVES = ((2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2))


def knight_moves(n, start, target):
    if start == target:
        return 0
    seen = {start}
    queue = deque([(start, 0)])
    while queue:
        (r, c), d = queue.popleft()
        for dr, dc in MOVES:
            nxt = (r + dr, c + dc)
            if 0 <= nxt[0] < n and 0 <= nxt[1] < n and nxt not in seen:
                if nxt == target:
                    return d + 1
                seen.add(nxt)
                queue.append((nxt, d + 1))
    return -1
```

On boards of size 1, 2 and 3 some squares cannot be reached (on `3 x 3` the centre has no legal move at all, and on `2 x 2` no move exists), so the queue empties and we return `-1`.

## Complexity

At most `n^2` squares, each with 8 moves: `O(n^2)` time and memory.

## Another way

Bidirectional BFS: grow a search from `start` and another from `target`, always expanding the smaller frontier, and stop when they meet; it visits far fewer squares on big boards. On an endless board there is even a formula, but the edges of a real board change the answer near the corners (`(0, 0) -> (1, 1)` needs 4 moves instead of 2), so the formula needs special cases. BFS is simpler and always right.
