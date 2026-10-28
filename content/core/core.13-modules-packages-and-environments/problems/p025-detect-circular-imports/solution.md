## Approach

A depth-first search does what the import system does: it goes as deep as possible before it finishes
a module. A module on the current path is *in progress*, like a partly initialised module in
`sys.modules`. Reaching an in-progress module again is a cycle; reaching a *done* module is a normal
shared dependency (a "diamond"). Appending a module when it is done gives a valid import order:
everything it imports was appended before it. One search gives both answers.

## Code

```python
NEW, IN_PROGRESS, DONE = 0, 1, 2


def _all_modules(graph):
    modules = set(graph)
    for imports in graph.values():
        modules.update(imports)
    return sorted(modules)


def _search(graph):
    state = {m: NEW for m in _all_modules(graph)}
    path = []
    order = []

    def visit(module):
        state[module] = IN_PROGRESS
        path.append(module)
        for dep in sorted(graph.get(module, [])):
            if state[dep] == IN_PROGRESS:
                return path[path.index(dep):] + [dep]
            if state[dep] == NEW:
                cycle = visit(dep)
                if cycle:
                    return cycle
        state[module] = DONE
        path.pop()
        order.append(module)
        return None

    for module in state:
        if state[module] == NEW:
            cycle = visit(module)
            if cycle:
                return order, cycle
    return order, None


def find_cycle(graph):
    return _search(graph)[1]


def import_order(graph):
    order, cycle = _search(graph)
    if cycle:
        raise ValueError("cycle: " + " -> ".join(cycle))
    return order
```

## Complexity

O(V + E log E) for V modules and E import arrows: every module and arrow is visited once, plus the
sorting. Memory O(V) for the states and the path.

## Another way

Kahn's algorithm: count for every module how many of its imports are not loaded yet, repeatedly take
the modules whose count is zero, and lower the counts of the modules that import them. If modules are
left at the end, they are in or behind a cycle. It needs no recursion, which helps for very deep
graphs (the default recursion limit is about 1000), but it does not tell you the cycle itself.

`graphlib.TopologicalSorter` in the standard library does this too, and its `CycleError` carries the
cycle. Real projects can use it; writing the DFS yourself shows what "partially initialised" means.
