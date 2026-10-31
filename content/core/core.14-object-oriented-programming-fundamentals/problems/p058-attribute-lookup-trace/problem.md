# Trace: instance dict, class attributes and properties

For `obj.name`, Python normally looks in the instance `__dict__` first and then in the class. But a
**property** on the class wins even over the instance `__dict__`. This trace mixes all the cases:
shadowing, deleting, a shared mutable class attribute, a property, and methods replaced on the instance
and on the class. Write the output in `answer.txt`.

```python
class Gadget:
    color = "grey"
    tags = []

    def __init__(self, name):
        self.name = name
        self._price = 100

    @property
    def price(self):
        print("getter runs")
        return self._price

    def label(self):
        return f"{self.name}:{self.color}"


g = Gadget("pen")
h = Gadget("cup")

print(g.color, h.color)
g.color = "red"
print(g.color, h.color, Gadget.color)
Gadget.color = "blue"
print(g.color, h.color)
del g.color
print(g.color, sorted(vars(g)))

g.tags.append("new")
h.tags = ["own"]
print(g.tags, h.tags, Gadget.tags)

g.__dict__["price"] = 5
print("price is", g.price)
print(vars(g)["price"])
try:
    g.price = 7
except AttributeError:
    print("cannot set price")

g.label = lambda: "replaced"
print(g.label(), h.label())
print(Gadget.label(g))
del g.label
print(g.label())

Gadget.label = lambda self: "class " + self.name
print(g.label(), h.label())
print(getattr(g, "size", "no size"), hasattr(g, "price"))
```

Facts you need:

- A property is a *data descriptor*: for reading **and** assigning, it is used even if the instance
  `__dict__` has a key with the same name. A property without a setter refuses assignment with
  `AttributeError`.
- Normal methods and plain class attributes lose against the instance `__dict__`.
- In `print(a, b)`, Python first evaluates `a` and `b`, then prints the line. Anything a getter
  prints appears **before** that line.
- `hasattr(obj, name)` works by trying `getattr(obj, name)`.

## Example of the format

```python
class C:
    x = 1

c = C()
c.x = 2
print(c.x, C.x, sorted(vars(c)))
```

prints

```text
2 1 ['x']
```
