# Explain: when is `__slots__` worth it?

A normal Python object stores its attributes in a dictionary. `__slots__` replaces that dictionary
by fixed storage. Here are two classes and a program that compares them.

```python
import sys


class PlainPoint:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class SlotPoint:
    __slots__ = ("x", "y")

    def __init__(self, x, y):
        self.x = x
        self.y = y


a, b = PlainPoint(1, 2), SlotPoint(1, 2)
print(hasattr(a, "__dict__"), hasattr(b, "__dict__"))
print(sys.getsizeof(a) + sys.getsizeof(a.__dict__), sys.getsizeof(b))
try:
    b.z = 3
except AttributeError as err:
    print("AttributeError:", err)
a.z = 3
print(a.z)
```

Output (the byte counts are from one machine and Python version; yours may differ):

```text
True False
344 48
AttributeError: 'SlotPoint' object has no attribute 'z' and no __dict__ for setting new attributes
3
```

In `answer.md` (about 200 to 350 words, plus a short code block), explain:

1. **What is different.** Where does a `PlainPoint` keep `x` and `y`, and where does a `SlotPoint`
   keep them? Why does `b.z = 3` fail while `a.z = 3` works?
2. **What you gain and give up.** Name at least two gains and at least two limits of `__slots__`.
3. **When it is worth it.** Describe a program where it clearly helps, and one where it does not.
4. **Measure first.** Show how you would measure the memory of 100,000 objects of each class before
   deciding.
