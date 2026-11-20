## Approach

```python
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
```

This is the model of chapter section 2.2: history is a DAG, and every commit points to its parents. A search that follows parent pointers collects everything the commit "contains". The `graph.get(c, [])` covers a parent missing from the log (a shallow clone).

Example: `ancestors(g, "d")`: start `{d}`; `d` has parent `m1`; `m1` has parents `b` and `c`; both lead to `a`. Result: `{d, m1, b, c, a}`.

## Complexity

`O(commits + parent links)`.

## Another way

A recursive version is shorter, but a long history (a chain of 100,000 commits) would hit the recursion limit. That is the reason the problem asks for a stack.
