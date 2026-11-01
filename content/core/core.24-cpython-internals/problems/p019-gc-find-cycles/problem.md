# Find the reference cycle

Reference counting frees an object the moment nothing refers to it, except when objects refer to
each other in a loop: a **reference cycle**. Then every count stays above zero and only the
cyclic garbage collector can free them. Cycles are often accidental (a child that points back at
its parent, a callback `self.handler = self.on_event` stored on the object itself), so it is
useful to ask: "is this object part of a cycle?"

`gc.get_referents(x)` returns the objects that `x` refers to directly (for a list: its items; for
a dict: its keys and values; for an instance: its attribute values, or its `__dict__`, and its
class). Following referents again and again walks the object graph. An object is in a cycle when
you can start at it, follow referents, and arrive back at the **same object** (`is`).

Copy `starter.py` to `solution.py` and write two functions.

**`cycle_path(obj, max_depth=100)`** returns the **shortest** path back to `obj` as a list of
objects `[obj, x1, x2, ..., obj]`, where each item is a referent of the one before it, or `None`
if there is no such path of at most `max_depth` steps. The direct referents of `obj` are 1 step
away, so `lst = []; lst.append(lst)` gives `[lst, lst]` (1 step).

**`in_cycle(obj, max_depth=100)`** returns `True` if `cycle_path` finds a path.

Rules for the walk:

- **Do not follow into** classes (`isinstance(x, type)`), modules (`types.ModuleType`) and plain
  functions (`types.FunctionType`). Every instance refers to its class, and every class and
  function leads to its module's globals, so following them would walk most of the program and
  find "cycles" through global variables that have nothing to do with your object.
- Visit each object at most once (compare by `id`), so the walk ends even inside other cycles.
- Search **breadth-first** (all objects 1 step away, then all 2 steps away, ...). A depth-first
  search with a "visited" set can mark an object as visited on a long path and then skip it on a
  shorter one, and wrongly answer `None` near the depth limit.

**Example**

```python
a, b = [], []
a.append(b)
b.append(a)
in_cycle(a)                  # True
cycle_path(a) == [a, b, a]   # True (compare with `is` to be exact)

class Node:
    def __init__(self):
        self.next = None

x, y, z = Node(), Node(), Node()
x.next = y; y.next = z; z.next = y      # y and z form a cycle; x only points into it
in_cycle(x), in_cycle(y)    # (False, True)
```

**Version note.** Whether the path through an instance contains its `__dict__` as a separate
step depends on the Python version (3.11 to 3.14 store instance attributes differently). The
tests only check paths made of lists exactly; for instances they check that each step really is a
referent of the previous one.
