# Custom __copy__ and __deepcopy__

The default `copy.copy` and `copy.deepcopy` treat every attribute the same way. Real objects
often need a policy per attribute. `starter.py` has a `Document` class with:

| attribute | meaning |
|---|---|
| `title` | a `str` |
| `lines`, `tags` | lists of `str` |
| `owner` | a `User` object: the person who owns the document |
| `links` | a list of other `Document`s (they may link back: cycles are possible) |
| `_cache` | derived data (`word_count` stores its result here) |

Copy `starter.py` to `solution.py` and write two methods:

1. `__copy__(self)`, used by `copy.copy(doc)`: a new document whose `lines` and `tags` are **new
   lists** (so editing the copy never changes the original), while `owner` and `links` are
   **shared** with the original. `_cache` is a new **empty** dict.
2. `__deepcopy__(self, memo)`, used by `copy.deepcopy(doc)`: everything is copied deeply
   (`lines`, `tags`, `links` and the linked documents) **except** `owner`, which stays the same
   `User` object (copying a document must not clone a person). `_cache` is a new empty dict.
   Cycles must work: if A links to B and B links back to A, the copy of B must link to the copy of A.

Both must work for subclasses: `copy.copy(draft)` returns a `Draft`, with any extra attributes
the subclass added. So do not call `Document(...)` and do not list the attributes by hand: copy
`self.__dict__`.

**Example**

```python
owner = User("Kavya")
doc = Document("Notes", ["hello world"], ["draft"], owner)
c = copy.copy(doc)
c.add_line("more")
doc.lines            # ['hello world']        (not shared)
c.owner is owner     # True

d = copy.deepcopy(doc)
d.owner is owner     # True                   (the default deepcopy would clone the User)
d.lines is doc.lines # False
```
