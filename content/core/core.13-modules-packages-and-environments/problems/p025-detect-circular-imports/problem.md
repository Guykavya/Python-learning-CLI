# Detect circular imports in a module graph

A circular import happens when module `a` imports `b`, `b` imports `c`, and `c` imports `a` again
before `a` has finished. In a big project the cycle can be long and hard to see. Tools such as
`pylint` (`cyclic-import`) find these cycles from a **graph** of imports.

The graph is a dict: each key is a module, and its value is the list of modules it imports at the top
level. A module that only appears in a list (like a standard library module) imports nothing.

```python
graph = {
    "app":     ["models", "views"],
    "views":   ["models", "utils"],
    "models":  ["db"],
    "db":      ["config"],
    "config":  [],
    "utils":   [],
}
```

Write two functions in `solution.py`.

### `find_cycle(graph)`

Return one cycle as a list of module names that starts and ends with the same module, for example
`["models", "db", "models"]`, following the import arrows. Return `None` if there is no cycle.
A module that imports itself is the cycle `["a", "a"]`.

### `import_order(graph)`

Return a list with **every** module (keys and modules that only appear in lists), each once, in an
order where every module comes **after** all the modules it imports. This is the order in which
Python finishes executing them. If the graph has a cycle, no such order exists: raise `ValueError`,
and put the cycle in the message joined with `" -> "` (for example `"cycle: a -> b -> a"`).

To make the answer the same every time, start from the modules in sorted order and visit the imports
of each module in sorted order.

### The method: depth-first search with three states

Walk the graph like Python walks imports. Give every module a state:

- **new**: not visited yet;
- **in progress**: we started it and are still inside its imports (it is on the current *path*);
- **done**: it and everything below it are finished.

Visiting a module: mark it in progress, add it to the path, visit each import. If an import is
**in progress**, you found a cycle: it is the part of the path from that module to the end, plus that
module again. After all its imports, mark it done, remove it from the path, and (for `import_order`)
append it to the result.

This is exactly the situation of a "partially initialised module" in Python: the module you reach is
still in progress.

## Example

```python
>>> import_order(graph)
['config', 'db', 'models', 'utils', 'views', 'app']
>>> find_cycle(graph) is None
True
>>> graph["config"] = ["models"]
>>> find_cycle(graph)
['models', 'db', 'config', 'models']
>>> import_order(graph)
Traceback (most recent call last):
ValueError: cycle: models -> db -> config -> models
```

(Your cycle may start at another module of the same loop, for example
`['db', 'config', 'models', 'db']`. Any correct cycle is accepted.)
