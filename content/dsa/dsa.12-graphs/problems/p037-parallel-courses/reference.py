from collections import deque


def min_semesters(n, relations):
    adj = [[] for _ in range(n)]
    indeg = [0] * n
    for u, v in relations:
        adj[u].append(v)
        indeg[v] += 1
    ready = deque(v for v in range(n) if indeg[v] == 0)
    rounds = done = 0
    while ready:
        rounds += 1
        for _ in range(len(ready)):                # exactly the courses of this semester
            u = ready.popleft()
            done += 1
            for v in adj[u]:
                indeg[v] -= 1
                if indeg[v] == 0:
                    ready.append(v)
    return rounds if done == n else -1
