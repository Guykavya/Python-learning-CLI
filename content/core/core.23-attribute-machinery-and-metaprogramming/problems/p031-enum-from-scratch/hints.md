## Hint 1

Sort the requirements by *whose* behaviour they are:

- Behaviour of **members** (`Color.RED.value`, `repr(Color.RED)`, `Color.RED.x = 1`): methods
  and properties on `MiniEnum`, because members are instances of `Color`, a subclass of `MiniEnum`.
- Behaviour of **the class** (`len(Color)`, `for c in Color`, `Color(2)`, `Color["RED"]`,
  `Color.RED = 5`): methods on `EnumMeta`, because `Color` is an instance of `EnumMeta`.

In `EnumMeta.__new__` you receive the namespace dict. Which entries are members? How do you
create a member without calling `Color(...)` (which you are about to turn into a lookup)?
And how do you set `_name` on a member if `MiniEnum.__setattr__` refuses every assignment?

## Hint 2

```
EnumMeta.__new__(mcls, name, bases, ns, **kw):
    if a base is an EnumMeta class with members: raise TypeError
    members = {k: v for k, v in ns.items() if k doesn't start with "_" and type(v) has no __get__}
    body    = ns without the member names
    cls = super().__new__(mcls, name, bases, body, **kw)
    type.__setattr__(cls, "_members", {})            # bypass your own __setattr__
    for key, value in members.items():
        if some existing member has == value: raise ValueError naming key
        m = object.__new__(cls)                      # no __call__, no __init__
        object.__setattr__(m, "_name", key)          # bypass MiniEnum.__setattr__
        object.__setattr__(m, "_value", value)
        cls._members[key] = m
        type.__setattr__(cls, key, m)
    return cls

EnumMeta: __iter__, __len__, __bool__ (True), __contains__ (identity), __getitem__,
          __call__(cls, value) -> lookup, __setattr__/__delattr__ refuse member names
MiniEnum: name/value properties, __setattr__/__delattr__ raise, __repr__, __str__
```
