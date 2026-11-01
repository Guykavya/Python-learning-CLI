## Approach

`ast.parse` does the hard work of turning text into a tree, and `ast.walk` flattens the tree
into a stream of nodes. Counting is then a one-line `Counter`. For `uses_name` the test is on
the node's *type*: only `ast.Name` nodes are variables, so strings, attributes and parameters
are skipped automatically.

## Code

```python
import ast
from collections import Counter


def count_nodes(source):
    tree = ast.parse(source)
    return Counter(type(node).__name__ for node in ast.walk(tree))


def uses_name(source, name):
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Name) and node.id == name:
            return True
    return False
```

## Complexity

O(n) in the number of nodes for both functions (plus parsing, which is linear in the source).

## Another way

`ast.NodeVisitor` calls `visit_<TypeName>` for each node you care about, and `generic_visit`
keeps walking into the children:

```python
class NameFinder(ast.NodeVisitor):
    def __init__(self, name):
        self.name = name
        self.found = False

    def visit_Name(self, node):
        if node.id == self.name:
            self.found = True
        self.generic_visit(node)


def uses_name(source, name):
    finder = NameFinder(name)
    finder.visit(ast.parse(source))
    return finder.found
```

The visitor is the better tool once you treat different node types differently (p029 uses its
cousin, `ast.NodeTransformer`).

**Version note.** `ast.dump` output differs slightly between versions (3.13+ hides default
fields such as `ctx=Load()`), so never compare dumps as text across versions. Node *types* such as
`Assign`, `BinOp`, `Name` and `Constant` are the same on 3.11 to 3.14.
