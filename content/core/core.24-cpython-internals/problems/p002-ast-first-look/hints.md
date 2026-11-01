## Hint 1

`ast.walk(tree)` already visits every node for you, at every depth. What do you need to collect
from each node to count types? And for `uses_name`, which two things must be true about a node
for it to count?

## Hint 2

```
count_nodes(source):
    tree = ast.parse(source)
    return Counter(type(node).__name__ for node in ast.walk(tree))

uses_name(source, name):
    for node in ast.walk(ast.parse(source)):
        if node is an ast.Name and node.id == name: return True
    return False
```
