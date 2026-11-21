## Approach

```python
def violations(sources, layers, package="taskboard"):
    found = set()
    for module, text in sources.items():
        if module not in layers:
            raise ValueError(f"module {module!r} is not in the layers table")
        my_layer = layers[module]
        project, external = _imports(ast.parse(text), package)
        for imported in project:
            if imported in layers and LAYER_RANK[layers[imported]] > LAYER_RANK[my_layer]:
                found.add((module, imported))
        for library in external:
            if library in EXTERNAL_BANS.get(my_layer, ()):
                found.add((module, library))
    return sorted(found)
```

`_imports` walks the tree with `ast.walk` (so imports inside functions count) and handles every spelling: relative (`from .repo import X`, `from . import repo`), absolute with the package name, and external libraries by their top-level name. The rule itself is two lines: **an inner layer must not depend on an outer one**, and **domain and services must not import the I/O libraries**. In the real project the same logic runs over the files of `taskboard/` in `tests/test_architecture.py` (chapter 10.2), and the demonstration "a quick fix imports `sqlite3` into the services" gives `['.repo', 'sqlite3']`.

## Complexity

O(size of the sources): one parse and one walk per module.

## Another way

Libraries such as `import-linter` (not installed here) express the same contracts in a configuration file ("layers: web, services, domain") and run them in CI. Writing it yourself once shows how little magic there is, and how a custom rule ("services must not import `sqlite3`") is easy to add.
