NEW, IN_PROGRESS, DONE = 0, 1, 2


def _all_modules(graph):
    modules = set(graph)
    for imports in graph.values():
        modules.update(imports)
    return sorted(modules)


def _search(graph):
    """Return (order, cycle). cycle is None when there is no cycle."""
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
