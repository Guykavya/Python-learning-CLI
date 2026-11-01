## Approach

Reproduce each report, then find the line responsible:

1. **Shared value.** `Field.__set__` does `self.value = value`. There is one `Field` per class
   attribute, shared by every instance, so the last assignment wins for all of them. Store in
   `instance.__dict__[self.name]`; `Field` is a data descriptor, so it still controls reads of
   that key.
2. **No name.** `self.name` is the constructor default `"field"`, because nobody passes a
   name. Add `__set_name__`, which Python calls at class creation with the real attribute
   name. (Fix 1 needs this too: two fields must not store under the same key.)
3. **Class access.** `Product.cost` calls `Alias.__get__(alias, None, Product)`, and
   `getattr(None, "price")` fails. Every `__get__` must handle `instance is None`, normally by
   returning `self`. Tools such as `help()`, `inspect` and test frameworks read attributes on the class, so a descriptor that crashes there breaks them sooner or later.
4. **Recursion.** `__getattr__` reads `self.extras`. When `extras` is missing (an object made by
   `copy` or `pickle` without `__init__`), that read itself calls `__getattr__("extras")`,
   which reads `self.extras`... until `RecursionError`. Read the instance dict directly with
   `vars(self)`, which never goes through `__getattr__`.

## Code

```python
class Field:
    def __init__(self, kind, default=MISSING):
        self.kind = kind
        self.default = default
        self.name = None

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        try:
            return instance.__dict__[self.name]
        except KeyError:
            if self.default is MISSING:
                raise AttributeError(f"{self.name} has not been set") from None
            return self.default

    def __set__(self, instance, value):
        if not isinstance(value, self.kind):
            raise TypeError(f"{self.name} must be {self.kind.__name__}, got {type(value).__name__}")
        instance.__dict__[self.name] = value


class Alias:
    def __init__(self, target):
        self.target = target

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        return getattr(instance, self.target)

    def __set__(self, instance, value):
        setattr(instance, self.target, value)


# in Model:
    def __getattr__(self, name):
        extras = vars(self).get("extras", {})
        if name in extras:
            return extras[name]
        raise AttributeError(f"{type(self).__name__} has no attribute or extra {name!r}")
```

`MISSING`, `Model.__init__` and `field_names` are unchanged.

## Complexity

All operations stay O(1) per attribute access (`field_names` is O(size of the class
hierarchy), as before).

## Another way

For bug 1, a `weakref.WeakKeyDictionary` on the descriptor (`self.values[instance] = value`)
also gives per-instance storage, without touching the instance dict; it works for classes with
`__slots__` but needs hashable instances, and a `copy` of the object does not get the values.
For bug 4, `if name == "extras": raise AttributeError(name)` at the top of `__getattr__`
also stops the recursion.

One more trap remains in this design: when an unset `Field` raises `AttributeError`, Python
falls back to `Model.__getattr__`, whose message (`has no attribute or extra 'y'`) replaces the
field's clearer `y has not been set`. That is the "AttributeError inside a descriptor triggers
`__getattr__`" rule from the chapter. A fix is to make `__getattr__` check
`name in self.field_names()` and say "has not been set" itself.
