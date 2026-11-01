## Approach

This is the first half of the attribute lookup algorithm, written out by hand:

1. Walk `cls.__mro__` and stop at the first class whose own `__dict__` has the name.
2. Take the **raw** object from that dict. `vars(owner)[name]` is a plain dict lookup, so no
   descriptor runs (unlike `getattr(cls, name)`, which calls `__get__(None, cls)`, or runs the
   metaclass's descriptors and `__getattr__`).
3. Ask the object's **type** which protocol methods it has. Python itself does exactly this:
   special methods are looked up on the type, so an instance attribute named `__set__` means nothing.

## Code

```python
def find_owner(cls, name):
    for klass in cls.__mro__:
        if name in vars(klass):
            return klass
    return None


def _type_defines(obj, method):
    # The protocol is looked up on the type, in the type's own MRO.
    return any(method in vars(klass) for klass in type(obj).__mro__)


def classify(cls, name):
    owner = find_owner(cls, name)
    if owner is None:
        return "missing"
    raw = vars(owner)[name]
    if _type_defines(raw, "__set__") or _type_defines(raw, "__delete__"):
        return "data descriptor"
    if _type_defines(raw, "__get__"):
        return "non-data descriptor"
    return "plain"


def describe(cls):
    return {name: classify(cls, name) for name in vars(cls) if not name.startswith("__")}
```

Results worth remembering: `property` is always a data descriptor (it has `__set__` even
without a setter; the `__set__` raises), slots are data descriptors (`member_descriptor`),
functions, `classmethod`, `staticmethod` and `cached_property` are non-data descriptors, and a
nested class is plain (`type` has no `__get__`).

## Complexity

`find_owner` is O(length of the MRO) dict lookups. `classify` adds O(length of the
descriptor type's MRO). `describe` is O(n × MRO) for n names.

## Another way

Use `hasattr` on the type, which searches the type's MRO for you:

```python
def classify(cls, name):
    owner = find_owner(cls, name)
    if owner is None:
        return "missing"
    t = type(owner.__dict__[name])
    if hasattr(t, "__set__") or hasattr(t, "__delete__"):
        return "data descriptor"
    return "non-data descriptor" if hasattr(t, "__get__") else "plain"
```

The standard library has `inspect.getattr_static(cls, name)`, which finds the raw object
without triggering descriptors, and `inspect.isdatadescriptor(obj)`. Writing them yourself
shows that there is no magic: just dicts and types.
