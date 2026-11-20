def parse_graph(text):
    graph = {}
    for line in text.splitlines():
        parts = line.split()
        if parts:
            graph[parts[0]] = parts[1:]
    return graph


def merge_commits(graph):
    return [sha for sha, parents in graph.items() if len(parents) >= 2]


def ancestors(graph, sha):
    seen = {sha}
    stack = [sha]
    while stack:
        c = stack.pop()
        for p in graph.get(c, []):
            if p not in seen:
                seen.add(p)
                stack.append(p)
    return seen
