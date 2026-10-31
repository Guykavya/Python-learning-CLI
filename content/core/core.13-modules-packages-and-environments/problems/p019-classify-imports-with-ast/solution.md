## Approach

Let Python's own parser find the imports. `ast.parse` turns the source into a tree, and
`ast.walk` visits every node, so imports inside functions and `try` blocks are found and text in
strings or comments is ignored. Both functions need the same scan, so one helper returns the set of
absolute top-level names and the set of relative imports. Classifying is then a simple order of
checks: local, then standard library, then third party.

## Code

```python
import ast
import sys


def _absolute_and_relative(source):
    absolute = set()
    relative = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            for alias in node.names:
                absolute.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.level == 0:
                absolute.add(node.module.split(".")[0])
            else:
                relative.add("." * node.level + (node.module or ""))
    return absolute, relative


def find_imports(source):
    absolute, _relative = _absolute_and_relative(source)
    return sorted(absolute)


def classify_imports(source, local=()):
    absolute, relative = _absolute_and_relative(source)
    local = set(local)
    groups = {"stdlib": set(), "third_party": set(), "local": set(relative)}
    for name in absolute:
        if name in local:
            groups["local"].add(name)
        elif name in sys.stdlib_module_names:
            groups["stdlib"].add(name)
        else:
            groups["third_party"].add(name)
    return {key: sorted(names) for key, names in groups.items()}
```

## Complexity

O(N) for N nodes in the tree, plus sorting the names.

## Another way

`importlib.util.find_spec(name)` can tell whether a module is installed *right now* and where it lives.
That answers a different question ("can I import it here?"), depends on the environment, and actually
imports parent packages. The `ast` scan reads the code without running anything, which is safer.

A third-party import name is not always the pip name: you `import yaml` but `pip install pyyaml`,
`import cv2` but `pip install opencv-python`. So this list is a starting point for your
dependencies, not the final answer.
