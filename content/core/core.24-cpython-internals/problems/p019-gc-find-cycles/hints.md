## Hint 1

This is a graph search where the nodes are objects and the edges are `gc.get_referents`. Which
search gives the shortest path, and what must you record for each object to rebuild that path at
the end? Objects may be unhashable (lists, dicts), so what can you use as a dictionary key for
"seen" and "came from"? When do you stop?

## Hint 2

```
parent = {}; seen = {}
frontier = [obj]
repeat max_depth times:
    next_frontier = []
    for node in frontier:
        for ref in gc.get_referents(node):
            if ref is obj:
                walk back from node using parent[id(...)] until you reach obj,
                build [obj, ..., node, obj] and return it
            if id(ref) in seen or ref is a class / module / function: skip
            seen[id(ref)] = ref; parent[id(ref)] = node
            next_frontier.append(ref)
    frontier = next_frontier (stop early if it is empty)
return None
```

Store the object itself in `seen` (not just its id): while you hold it, its `id` cannot be reused
by a new object.
