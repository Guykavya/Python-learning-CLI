## Hint 1

Picture Python importing `app`: it starts `app`, which starts `models`, which starts `db`... At any
moment there is a chain of modules that are started but not finished. If an import points at a
module **in that chain**, what has happened? And if it points at a module that already finished, is
that a problem?

## Hint 2

```text
modules = sorted(keys + everything in the lists); state[m] = NEW for all
path = []; order = []

visit(m):
    state[m] = IN_PROGRESS; path.append(m)
    for dep in sorted(graph.get(m, [])):
        if state[dep] == IN_PROGRESS: return path[path.index(dep):] + [dep]   # cycle
        if state[dep] == NEW: cycle = visit(dep); if cycle: return cycle
    state[m] = DONE; path.pop(); order.append(m)
    return None

for m in modules: if state[m] == NEW: cycle = visit(m); if cycle: stop
```

`find_cycle` returns the cycle (or `None`); `import_order` raises if there is a cycle, else returns `order`.
