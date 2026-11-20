## Approach

Turning the story into a graph does most of the work: people are vertices and each dislike is an edge. A split into two groups with no dislike inside a group is a **two-colouring**: exactly the bipartite check of chapter section 8. This time we return the colours.

Inside a connected piece, the first person's group forces everyone else's: BFS spreads opposite colours along the edges. If an edge ever joins two people of the same colour, the forced choices contradict each other (there is an odd cycle of dislikes, see p042), so no split exists. Pieces are independent: each starts with colour 0. A lonely person is a piece by themself and simply gets 0.

```python
from collections import deque


def two_colour(n, dislikes):
    adj = [[] for _ in range(n)]
    for a, b in dislikes:
        adj[a].append(b)
        adj[b].append(a)
    group = [-1] * n
    for s in range(n):
        if group[s] != -1:
            continue
        group[s] = 0
        queue = deque([s])
        while queue:
            u = queue.popleft()
            for v in adj[u]:
                if group[v] == -1:
                    group[v] = 1 - group[u]
                    queue.append(v)
                elif group[v] == group[u]:
                    return None                    # two enemies forced into one group
    return group
```

## Complexity

`O(n + E)` time and memory.

## Another way

Union-Find with "enemy" groups: for each person `u`, everyone `u` dislikes must end up together (in the group opposite to `u`). Unite all of `u`'s enemies with each other; if `u` is ever in the same set as one of its enemies, return `None`. Reading the colours out of the sets takes one more pass. BFS is simpler here.
