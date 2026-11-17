# Fix the cycle detector

A build tool must refuse a project whose modules import each other in a circle. A teammate wrote the check. The graph is a dictionary: `graph[m]` is the list of modules that `m` imports (every module is a key, also when it imports nothing). It is in `starter.py`:

```python
def has_cycle(graph):
    """True if the import graph has a directed cycle."""
    visited = set()

    def visit(u):
        visited.add(u)
        for v in graph[u]:
            if v in visited or visit(v):
                return True
        return False

    return any(u not in visited and visit(u) for u in graph)
```

It passes the teammate's tests:

```python
>>> has_cycle({"a": ["b"], "b": ["c"], "c": ["a"]})       # a real circle
True
>>> has_cycle({"a": ["b"], "b": [], "c": []})
False
```

But users complain that the tool refuses perfectly good projects, for example:

```python
>>> has_cycle({"app": ["db", "web"], "db": ["util"], "web": ["util"], "util": []})
False                         # expected; the starter says True
```

1. Run the starter on the complaint. Which edge makes it return `True`? Is there a way to follow imports from `util` back to `app`?
2. "I have seen this module before" proves a cycle in an **undirected** graph (chapter section 6). Why not in a **directed** one?
3. Fix the function. Keep the signature and the recursive style if you like (the test graphs are at most 400 modules deep), or rewrite it with a stack.

## Rules for the fixed function

- Return `True` exactly when you can follow imports from some module back to itself. A module that imports itself (`{"x": ["x"]}`) is a cycle.
- It must be **fast**: one test is a layered project (40 layers of 4 modules, each importing every module of the next layer). It has no cycle, but more than `10**23` different import paths. A fix that explores a module again every time it is reached runs forever; the test stops it after 10 seconds.

## Think about

Which three states can a module be in during the DFS? Which state means "on the path I am walking right now", and which means "already fully checked, safe"?
