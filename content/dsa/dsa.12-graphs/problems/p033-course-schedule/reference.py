from collections import deque


def can_finish(num_courses, prerequisites):
    adj = [[] for _ in range(num_courses)]
    indeg = [0] * num_courses
    for a, b in prerequisites:
        adj[b].append(a)                           # b must come before a
        indeg[a] += 1
    ready = deque(c for c in range(num_courses) if indeg[c] == 0)
    taken = 0
    while ready:
        c = ready.popleft()
        taken += 1
        for d in adj[c]:
            indeg[d] -= 1
            if indeg[d] == 0:
                ready.append(d)
    return taken == num_courses
