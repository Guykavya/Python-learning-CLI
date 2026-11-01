# What does this object keep alive? Walking the object graph

An object stays alive as long as something refers to it, so one forgotten root (a cache, a
global list, a listener) can keep a whole tree of objects in memory. `gc.get_referents(obj)`
returns the objects that `obj` refers to directly (for a list: its items; for an object: its
attribute values, and its class). Following it again and again walks the **object graph**,
which is how memory tools find out what a root keeps alive.

Copy `starter.py` to `solution.py` and write:

**`kind(obj)`** decides what to do with an object:

- `"follow"` for a plain `dict` (`type(obj) is dict`): walk through its values, but do not count it;
- `"count"` for a `list`, `tuple`, `set` or `frozenset`, and for **user objects**: anything that
  is not a type, function, builtin function, method or module (`NEVER_FOLLOW`) and whose type is not
  a builtin type (`type(obj).__module__ != "builtins"`);
- `None` for everything else (strings, numbers, `None`, classes, functions, modules...): do not
  count it and do not follow it. Classes, functions and modules lead to the whole program.

**`reachable(root, max_nodes=10_000)`** walks the graph **breadth-first** from `root` with
`gc.get_referents`, visits every object at most once (remember ids, so cycles end), and returns
the list of `"count"` objects in the order they were reached, the root first. Stop as soon as
`max_nodes` objects have been found. Use a queue, not recursion (a long linked list would
exceed the recursion limit).

**`summary(root, max_nodes=10_000)`** returns a `Counter` of the type names of
`reachable(root, max_nodes)`.

**Why are dicts followed but not counted?** Since Python 3.11, CPython keeps an instance's
attribute values in a compact array and creates a real `__dict__` object only when someone asks
for it (`vars(obj)`, `obj.__dict__`); since 3.13 the values even live inside the object itself.
So `gc.get_referents(obj)` returns either the dict or the attribute values directly, depending on
the version and on what your code did before. Walking *through* dicts without counting them
gives the same summary in every case.

**Example**

```python
class Node:
    def __init__(self, value=None, next=None):
        self.value = value
        self.next = next

c = Node([1, 2])
b = Node((3, 4), c)
a = Node({"x": {5}}, b)
c.next = a                      # a cycle: a -> b -> c -> a

>>> summary(a) == {"Node": 3, "list": 1, "tuple": 1, "set": 1}
True
>>> reachable(a)[0] is a
True
>>> summary(chain_of_100_nodes, max_nodes=10)
Counter({'Node': 10})
```
