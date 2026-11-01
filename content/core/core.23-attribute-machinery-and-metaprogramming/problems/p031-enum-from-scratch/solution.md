## Approach

An enum is two layers of objects, and each layer gets its behaviour from its own type:

| Object | Its type | So its behaviour is defined in |
|---|---|---|
| `Color.RED` | `Color` (subclass of `MiniEnum`) | `MiniEnum` |
| `Color` | `EnumMeta` | `EnumMeta` |

`len(Color)` calls `type(Color).__len__(Color)`, which is `EnumMeta.__len__`. `Color(2)` calls
`EnumMeta.__call__`, and since we never call `super().__call__` there, no new instance is ever
created by calling the class; members are made once, with `object.__new__(cls)`, while the
class is built.

Members are found in the class namespace, the dict the class body ran in. A value is a member
if its name is public and it is not a descriptor: functions, properties, `classmethod` and
`staticmethod` all have `__get__` on their type, which is exactly what makes them methods.
We remove the members from the namespace before `type.__new__` so the class first gets only the
methods; then we create each member and store it on the class.

## Code

```python
class EnumMeta(type):
    def __new__(mcls, name, bases, ns, **kwargs):
        for base in bases:
            if isinstance(base, EnumMeta) and len(base):
                raise TypeError(f"cannot extend {base.__name__}: it has members")
        members = {
            key: value
            for key, value in ns.items()
            if not key.startswith("_") and not hasattr(type(value), "__get__")
        }
        body = {key: value for key, value in ns.items() if key not in members}
        cls = super().__new__(mcls, name, bases, body, **kwargs)
        type.__setattr__(cls, "_members", {})
        for key, value in members.items():
            for other in cls._members.values():
                if other._value == value:
                    raise ValueError(f"duplicate value {value!r} for {key} in {name} (already used by {other._name})")
            member = object.__new__(cls)
            object.__setattr__(member, "_name", key)
            object.__setattr__(member, "_value", value)
            cls._members[key] = member
            type.__setattr__(cls, key, member)
        return cls

    def __iter__(cls):
        return iter(list(cls._members.values()))

    def __len__(cls):
        return len(cls._members)

    def __bool__(cls):
        return True

    def __contains__(cls, member):
        return any(member is m for m in cls._members.values())

    def __getitem__(cls, name):
        return cls._members[name]

    def __call__(cls, value):
        for member in cls._members.values():
            if member._value == value:
                return member
        raise ValueError(f"{value!r} is not a valid {cls.__name__}")

    def __setattr__(cls, name, value):
        if name in vars(cls).get("_members", {}):
            raise AttributeError(f"cannot reassign member {name}")
        super().__setattr__(name, value)

    def __delattr__(cls, name):
        if name in vars(cls).get("_members", {}):
            raise AttributeError(f"cannot delete member {name}")
        super().__delattr__(name)


class MiniEnum(metaclass=EnumMeta):
    @property
    def name(self):
        return self._name

    @property
    def value(self):
        return self._value

    def __setattr__(self, name, value):
        raise AttributeError(f"{type(self).__name__} members are immutable")

    def __delattr__(self, name):
        raise AttributeError(f"{type(self).__name__} members are immutable")

    def __repr__(self):
        return f"<{type(self).__name__}.{self._name}: {self._value!r}>"

    def __str__(self):
        return f"{type(self).__name__}.{self._name}"
```

Details that matter:

- `type.__setattr__(cls, ...)` and `object.__setattr__(member, ...)` skip our own blocking
  `__setattr__` methods. That is the standard way to build an object that is immutable afterwards.
- `__bool__` on the metaclass: without it, `bool(Color)` falls back to `len(Color)`, so an enum
  with no members would be falsy and `if SomeEnum:` would surprise everybody.
- Duplicates are checked with `==` and a loop, not a dict, so unhashable values such as lists still work.

## Complexity

Creating the class is O(n²) for n members (the duplicate check), which is fine for enums. Lookup
by value and `in` are O(n); lookup by name is O(1). Keeping a second dict from value to member
would make `Color(2)` O(1) for hashable values.

## Another way

Create the members in the metaclass `__init__` instead of `__new__` (the class is complete
there too), keep them in a tuple, and search it for name lookups. The real `enum` module goes
further: it uses `__prepare__` to return a special dict that detects a name defined twice in the
body (`RED = 1` then `RED = 2`), which a plain dict silently overwrites. That is something only a
metaclass can do.
