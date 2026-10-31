## Approach

All three bugs are the same idea: **a default is evaluated once**, and an object evaluated once is shared. In `Cart`, the default list belongs to the function object and every call without `items` uses it. In `Tags`, `set()` is evaluated at class-definition time and produces an object where a function was needed, so creating a `Tags()` fails when the dataclass tries to call it. In `Counter`, the lambda is a proper factory, but it returns the same global dict each time.

`field(default_factory=...)` is the tool for "a new object each time": it stores a function that the generated `__init__` calls for every new instance that was not given a value. The built-in types `list`, `set` and `dict` are already such functions.

## Code

```python
from dataclasses import dataclass, field


@dataclass
class Cart:
    owner: str
    items: list = field(default_factory=list)

    def add(self, item):
        self.items.append(item)

    def count(self):
        return len(self.items)


@dataclass
class Tags:
    names: set = field(default_factory=set)

    def add(self, name):
        self.names.add(name.lower())


@dataclass
class Counter:
    counts: dict = field(default_factory=dict)

    def hit(self, key):
        self.counts[key] = self.counts.get(key, 0) + 1
```

## Complexity

No change: all operations are O(1) average.

## Another way

For plain classes, the fix is `def __init__(self, owner, items=None): self.items = [] if items is None else items`. Converting to dataclasses is shorter and gives `repr` and `==` for free.
