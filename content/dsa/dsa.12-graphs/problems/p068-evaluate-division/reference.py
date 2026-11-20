from collections import defaultdict, deque


def evaluate(equations, values, queries):
    adj = defaultdict(list)
    for (a, b), k in zip(equations, values):
        adj[a].append((b, k))
        adj[b].append((a, 1 / k))
    answers = []
    for x, y in queries:
        if x not in adj or y not in adj:
            answers.append(-1.0)
            continue
        product = {x: 1.0}
        queue = deque([x])
        while queue and y not in product:
            u = queue.popleft()
            for v, k in adj[u]:
                if v not in product:
                    product[v] = product[u] * k
                    queue.append(v)
        answers.append(product.get(y, -1.0))
    return answers
