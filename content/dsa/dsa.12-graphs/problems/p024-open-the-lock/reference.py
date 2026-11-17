from collections import deque


def open_lock(deadends, target):
    k = len(target)
    dead = set(deadends)
    start = "0" * k
    if start in dead:
        return -1
    dist = {start: 0}
    queue = deque([start])
    while queue:
        state = queue.popleft()
        if state == target:
            return dist[state]
        for i in range(k):
            digit = int(state[i])
            for step in (1, -1):
                nxt = state[:i] + str((digit + step) % 10) + state[i + 1:]
                if nxt not in dead and nxt not in dist:
                    dist[nxt] = dist[state] + 1
                    queue.append(nxt)
    return -1
