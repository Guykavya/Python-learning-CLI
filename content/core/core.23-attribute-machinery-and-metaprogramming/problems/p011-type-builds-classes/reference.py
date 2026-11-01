def make_record_class(name, fields):
    fields = tuple(fields)

    def __init__(self, *values):
        if len(values) != len(fields):
            raise TypeError(
                f"{name} expects {len(fields)} values ({', '.join(fields)}), got {len(values)}"
            )
        for field, value in zip(fields, values):
            setattr(self, field, value)

    def __repr__(self):
        parts = ", ".join(f"{field}={getattr(self, field)!r}" for field in fields)
        return f"{type(self).__name__}({parts})"

    def __eq__(self, other):
        if type(other) is not type(self):
            return NotImplemented
        return all(getattr(self, f) == getattr(other, f) for f in fields)

    namespace = {
        "__slots__": fields,
        "__init__": __init__,
        "__repr__": __repr__,
        "__eq__": __eq__,
    }
    return type(name, (), namespace)
