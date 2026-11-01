REQUIRED = ("table", "fields")


class Record:
    """Base class for table records. Subclasses must define `table` and `fields`."""

    def __init_subclass__(cls, /, abstract=False, **kwargs):
        super().__init_subclass__(**kwargs)
        if abstract:
            return
        missing = sorted(name for name in REQUIRED if not hasattr(cls, name))
        if missing:
            raise TypeError(f"{cls.__name__} is missing class attribute(s): {', '.join(missing)}")
        if not isinstance(cls.table, str) or not cls.table:
            raise TypeError(f"{cls.__name__}.table must be a non-empty str")
        fields = cls.fields
        if not isinstance(fields, tuple) or not fields or not all(isinstance(f, str) for f in fields):
            raise TypeError(f"{cls.__name__}.fields must be a non-empty tuple of str")
        if len(set(fields)) != len(fields):
            raise TypeError(f"{cls.__name__}.fields has duplicate names")

    def __init__(self, **values):
        name = type(self).__name__
        missing = [f for f in self.fields if f not in values]
        if missing:
            raise TypeError(f"{name} missing field(s): {', '.join(missing)}")
        unknown = [key for key in values if key not in self.fields]
        if unknown:
            raise TypeError(f"{name} got unknown field(s): {', '.join(unknown)}")
        for field in self.fields:
            setattr(self, field, values[field])

    def __repr__(self):
        args = ", ".join(f"{f}={getattr(self, f)!r}" for f in self.fields)
        return f"{type(self).__name__}({args})"
