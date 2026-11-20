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


def merge_kind(graph, current, other):
    if other in ancestors(graph, current):
        return "up-to-date"
    if current in ancestors(graph, other):
        return "fast-forward"
    return "merge"
