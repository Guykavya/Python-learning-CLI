**1. What is different.** A normal object keeps its attributes in a dictionary, `obj.__dict__`, created for every object. That is why `a.z = 3` works for any new name at any time, and also why `PlainPoint` shows `True` for `hasattr(a, "__dict__")`. A class with `__slots__ = ("x", "y")` has **no** `__dict__` (`False`); the two attributes live in fixed slots inside the object, like fields of a C struct. Setting `b.z` therefore fails with `AttributeError`: there is nowhere to store it. In the example one plain point used 344 bytes (object plus its dict) and the slotted one 48 bytes on one machine (numbers differ between Python versions).

**2. What you gain and give up.** Gain: much less memory per object (no dict per object) and slightly faster attribute access. Typos like `p.zz = 1` become errors instead of silent new attributes. Give up: no new attributes at run time, no `vars(obj)`, no weak references unless you add `"__weakref__"`, and problems with multiple inheritance when more than one parent has non-empty slots. A subclass that does not declare `__slots__` gets a `__dict__` again.

**3. When it is worth it.** When you create **very many** small objects of one class: a million points, nodes of a tree or linked list, records read from a big file. Saving ~200-300 bytes each gives hundreds of megabytes. For a handful of objects (a config, a few services) it is not worth losing flexibility.

**4. Measure first.**

```python
import tracemalloc
tracemalloc.start()
points = [SlotPoint(i, i) for i in range(100_000)]
print(tracemalloc.get_traced_memory()[0])
```

Run it for both classes and compare. Without a measurement you do not know that memory is your problem, and the extra rules of `__slots__` cost readability. Also consider alternatives: a tuple or `NamedTuple` for read-only records, or a dataclass with `slots=True`.
