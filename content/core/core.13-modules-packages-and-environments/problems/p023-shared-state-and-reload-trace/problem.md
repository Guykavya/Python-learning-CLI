# Trace: shared module state, from-imports and reload

Every importer of a module gets the **same** module object from the cache. But `from m import x`
copies a *binding*: it makes a new name that points at the same object. What happens with a list
(mutable, shared) and an int (immutable, rebound)? And what does `importlib.reload` do to the
names other modules copied?

Four files in one folder:

`registry.py`:

```python
print("registry runs")
items = []
count = 0


def add(name):
    global count
    items.append(name)
    count += 1
```

`a.py`:

```python
import registry

registry.add("a")
print("a sees", registry.items, registry.count)
```

`b.py`:

```python
from registry import items, count, add

add("b")
items.append("b2")
count += 100
print("b sees", items, count)
```

`main.py`:

```python
import importlib

import a
import b
import registry
import a

print("main sees", registry.items, registry.count)
print("b.count =", b.count, "| same list?", b.items is registry.items)

importlib.reload(registry)
registry.add("c")
print("after reload:", registry.items, registry.count)
print("b still has", b.items, "| same list?", b.items is registry.items)
b.add("d")
print("b.add went to", registry.items, "| b.items is", b.items)
```

Kavya runs `python main.py`. Write exactly what it prints, one line per printed line, in
`answer.txt`. The program never stops with an error.

One fact you need: `importlib.reload(m)` runs the file of `m` again **inside the same module
object**. Its names are overwritten with new objects, but the module object (and its globals
dictionary) stays the same.

## Example of the format

`print("x", [1, 2], 3)` prints `x [1, 2] 3`.
