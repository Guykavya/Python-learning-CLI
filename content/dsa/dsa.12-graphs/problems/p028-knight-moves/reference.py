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
