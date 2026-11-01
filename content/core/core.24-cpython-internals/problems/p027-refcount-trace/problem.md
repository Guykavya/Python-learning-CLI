# Trace: when does an object die?

CPython frees an object the moment its **reference count** drops to zero. A
`weakref.ref(obj)` lets you watch this without keeping the object alive: calling the weak
reference returns the object while it lives and `None` once it has been freed.

The program below never prints a refcount (those numbers differ between Python versions). It
only asks "alive or dead?" after each step. Predict every line **without running it**.

Facts you may need (not the answer):

- `del name` removes a **name**, not an object. Rebinding a name (`b = ...`) also drops one
  reference to the old object.
- A list holds one reference per slot, a dict one per value. A function's local variables are
  references held by its frame, and the frame goes away when the function returns.
- `gc.disable()` turns off only the *automatic* cycle collector. Reference counting keeps working,
  and `gc.collect()` still runs a collection when you call it. It returns the number of
  unreachable objects it found.
- This is the behaviour of the standard CPython build, 3.11 to 3.14.

```python
import gc
import weakref


class Node:
    def __init__(self, name):
        self.name = name
        self.other = None


def state(ref):
    return "alive" if ref() is not None else "dead"


gc.disable()   # only reference counting frees objects below, until gc.collect() is called

a = Node("a")
ra = weakref.ref(a)
b = a
del a
print(1, state(ra), b.name)
b = Node("b")
print(2, state(ra), ra() is None)

c = Node("c")
rc = weakref.ref(c)
box = [c, c]
del c
print(3, state(rc), len(box))
box.pop()
print(4, state(rc))
box.clear()
print(5, state(rc))

table = {"k": Node("d")}
rd = weakref.ref(table["k"])
print(6, state(rd))
table["k"] = "replaced"
print(7, state(rd))


def make():
    local = Node("local")
    return weakref.ref(local)


rl = make()
print(8, state(rl))


def keep():
    local = Node("kept")
    return local, weakref.ref(local)


kept, rk = keep()
print(9, state(rk), rk().name)
kept = None
print(10, state(rk))

x = Node("x")
y = Node("y")
x.other = y
y.other = x
rx = weakref.ref(x)
ry = weakref.ref(y)
del x
print(11, state(rx), state(ry))
del y
print(12, state(rx), state(ry))
found = gc.collect()
print(13, state(rx), state(ry), found > 0)
gc.enable()
```

**Example**: the first line is

```
1 alive a
```

`a` and `b` named the same object; `del a` removed only one of the two names.

Write in `answer.txt` all the lines the program prints, in order (13 lines).
