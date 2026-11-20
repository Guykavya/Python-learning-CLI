import heapq


def prim(n, edges):
    adj = [[] for _ in range(n)]
    for u, v, w in edges:
        adj[u].append((w, u, v))
        adj[v].append((w, v, u))
    in_tree = [False] * n
    in_tree[0] = True
    heap = list(adj[0])
    heapq.heapify(heap)
    tree, total = [], 0
    while heap and len(tree) < n - 1:
        w, u, v = heapq.heappop(heap)
        if in_tree[v]:
            continue
        in_tree[v] = True
        tree.append((u, v, w))
        total += w
        for item in adj[v]:
            if not in_tree[item[2]]:
                heapq.heappush(heap, item)
    if len(tree) < n - 1:
        return None
    return total, tree
