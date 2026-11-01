## Hint 1

`__class_getitem__(cls, item_type)` can return any object. Which built-in creates a class
from a name, a tuple of bases and a dict of attributes? Where can you remember the classes you
already made, so the second `TypedList[int]` finds the first one? In `append`, how do you reach
the checked type from `self`?

## Hint 2

```
class TypedList(list):
    item_type = object
    _cache = {}

    __class_getitem__(cls, item_type):
        if item_type is not a class: raise TypeError
        if item_type not in the cache:
            cache[item_type] = type(f"TypedList[{item_type.__name__}]", (TypedList,), {"item_type": item_type})
        return cache[item_type]

    _check(item): if not isinstance(item, self.item_type): raise TypeError(expected, got)
    __init__(items=()): items = list(items); check each; super().__init__(items)
    append(item): check; super().append(item)
```
