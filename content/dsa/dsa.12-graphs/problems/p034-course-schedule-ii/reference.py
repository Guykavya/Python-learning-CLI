from collections import deque


def find_order(num_courses, prerequisites):
    adj = [[] for _ in range(num_courses)]
    indeg = [0] * num_courses
    for a, b in prerequisites:
        adj[b].append(a)                           # b before a
        indeg[a] += 1
    ready = deque(c for c in range(num_courses) if indeg[c] == 0)
    order = []
    while ready:
        c = ready.popleft()
        order.append(c)
        for d in adj[c]:
            indeg[d] -= 1
            if indeg[d] == 0:
                ready.append(d)
    return order if len(order) == num_courses else []
