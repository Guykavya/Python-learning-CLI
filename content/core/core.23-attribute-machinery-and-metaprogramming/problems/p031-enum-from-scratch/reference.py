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
