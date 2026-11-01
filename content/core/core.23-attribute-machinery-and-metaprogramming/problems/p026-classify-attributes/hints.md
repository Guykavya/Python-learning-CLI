## Hint 1

Where does an attribute *physically live*? In the `__dict__` of one class (see it with
`vars(klass)`). `cls.__mro__` lists the classes in the order Python searches them. So
`find_owner` is a loop that asks `name in vars(klass)`. Reading `vars(klass)[name]` gives you the
**raw** object (the property itself, the function itself) without running any `__get__`.

Then: how do you ask "does this object's **type** define `__set__`"? Not on the object, on `type(obj)`.

## Hint 2

```
find_owner(cls, name):
    for klass in cls.__mro__:
        if name in vars(klass): return klass
    return None

classify(cls, name):
    owner = find_owner(cls, name);  if None -> "missing"
    raw = vars(owner)[name]
    t = type(raw)
    if t has __set__ or __delete__   -> "data descriptor"
    elif t has __get__               -> "non-data descriptor"
    else                             -> "plain"

describe(cls):
    {name: classify(cls, name) for name in vars(cls) if name does not start with "__"}
```

`hasattr(t, "__set__")` on the type `t` is fine: it looks in `t`'s own MRO, so inherited
`__set__` counts. (Looking at `t`'s metaclass does not matter here.)
