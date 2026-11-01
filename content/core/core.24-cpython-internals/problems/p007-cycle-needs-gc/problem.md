# Trace: a cycle needs the garbage collector

CPython frees most objects through **reference counting**: the moment the last reference goes
away, the object is freed. Objects that point at each other in a **cycle** keep each other's
count above zero even when your program can no longer reach them. Those are found later by the
**cyclic garbage collector** (`gc`), which runs from time to time, or right now when you call
`gc.collect()`.

To watch an object die without keeping it alive, use a **weak reference**:
`r = weakref.ref(obj, callback)`. Calling `r()` gives the object, or `None` once it has been
freed, and `callback(r)` is called at the moment the object is freed.

The program below turns the automatic collector off with `gc.disable()` so that it only runs
when we ask. Work out exactly what it prints. The program needs no input.

```python
import gc
import weakref


class Node:
    def __init__(self, name):
        self.name = name
        self.partner = None


def gone(ref):
    print("freed")


def main():
    gc.disable()
    a = Node("a")
    b = Node("b")
    a.partner = b
    b.partner = a
    ra = weakref.ref(a, gone)
    rb = weakref.ref(b, gone)
    print(ra() is a, rb().name, rb().partner.name)
    del a
    print("after del a:", ra() is None)
    del b
    print("after del b:", ra() is None, rb() is None)
    found = gc.collect()
    print("collected:", found > 0)
    print("after collect:", ra() is None, rb() is None)
    c = Node("c")
    rc = weakref.ref(c, gone)
    del c
    print("no cycle:", rc() is None)
    gc.enable()


main()
```

Write your answer in `answer.txt`, one output line per line of output. Remember that the
callback prints too.

**Example (a different program)**

```python
import weakref

class Thing:
    pass

def bye(ref):
    print("bye")

t = Thing()
r = weakref.ref(t, bye)
t = None
print(r() is None)
```

prints

```
bye
True
```
