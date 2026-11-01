## Approach

Subscription is just a method call, `TypedList.__class_getitem__(int)`. We build a subclass with
`type(name, bases, namespace)`, store `item_type` in it as a class attribute, and keep the result
in a dict so the same parameter always gives the same class (otherwise `isinstance` against
`TypedList[int]` would fail for objects made by an earlier `TypedList[int]`). The instances look
up `self.item_type`, which is found on their class.

## Code

```python
class TypedList(list):
    item_type = object
    _cache = {}

    def __class_getitem__(cls, item_type):
        if not isinstance(item_type, type):
            raise TypeError(f"TypedList[...] needs a class, got {item_type!r}")
        if item_type not in TypedList._cache:
            name = f"TypedList[{item_type.__name__}]"
            sub = type(name, (TypedList,), {"item_type": item_type})
            TypedList._cache[item_type] = sub
        return TypedList._cache[item_type]

    def _check(self, item):
        if not isinstance(item, self.item_type):
            raise TypeError(
                f"{type(self).__name__} expects {self.item_type.__name__}, got {type(item).__name__}"
            )

    def __init__(self, items=()):
        items = list(items)          # read a generator only once
        for item in items:
            self._check(item)
        super().__init__(items)

    def append(self, item):
        self._check(item)
        super().append(item)
```

## Complexity

`TypedList[T]`: O(1) after the first time (dict lookup). `append`: O(1). `__init__`: O(n).

## Another way

Put the class factory in a function wrapped with `functools.cache`, which does the
"same input, same result" caching for you, and create the subclass with a `class` statement
inside it, then set `__name__`. Checking in `__init__` by calling `self.append` for each item
also works and reuses the one check.

Should you do this in real code? Usually not: `list[int]` plus a type checker (mypy, pyright)
catches these mistakes before the program runs, for free. Runtime-checked containers are worth it
only at trust boundaries, such as data coming from users or files.
