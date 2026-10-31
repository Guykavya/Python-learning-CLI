class FieldError(Exception):
    def __init__(self, field, message):
        self.field = field
        self.message = message
        super().__init__(f"{field}: {message}")


class Field:
    def __init__(self, *, required=True, default=None):
        self.required = required
        self.default = default

    def check(self, name, value):
        if value is None:
            if self.default is not None:
                return self.default
            if self.required:
                raise FieldError(name, "is required")
            return None
        return value


class IntField(Field):
    def __init__(self, *, min_value=None, max_value=None, **kwargs):
        super().__init__(**kwargs)
        self.min_value = min_value
        self.max_value = max_value

    def check(self, name, value):
        if value is None:
            return super().check(name, value)
        if not isinstance(value, int) or isinstance(value, bool):
            raise FieldError(name, "must be an int")
        if self.min_value is not None and value < self.min_value:
            raise FieldError(name, f"must be >= {self.min_value}")
        if self.max_value is not None and value > self.max_value:
            raise FieldError(name, f"must be <= {self.max_value}")
        return value


class StrField(Field):
    def __init__(self, *, min_length=0, max_length=None, choices=None, **kwargs):
        super().__init__(**kwargs)
        self.min_length = min_length
        self.max_length = max_length
        self.choices = choices

    def check(self, name, value):
        if value is None:
            return super().check(name, value)
        if not isinstance(value, str):
            raise FieldError(name, "must be a str")
        if len(value) < self.min_length:
            raise FieldError(name, f"length must be >= {self.min_length}")
        if self.max_length is not None and len(value) > self.max_length:
            raise FieldError(name, f"length must be <= {self.max_length}")
        if self.choices is not None and value not in self.choices:
            raise FieldError(name, "must be one of: " + ", ".join(self.choices))
        return value


class Model:
    @classmethod
    def fields(cls):
        result = {}
        for klass in reversed(cls.__mro__):
            for name, value in vars(klass).items():
                if isinstance(value, Field):
                    result[name] = value
        return result

    def __init__(self, **values):
        fields = self.fields()
        for name in values:
            if name not in fields:
                raise TypeError(f"unknown field {name!r}")
        for name in fields:
            setattr(self, name, values.get(name))

    def validate(self):
        cleaned = {}
        errors = []
        for name, field in self.fields().items():
            try:
                cleaned[name] = field.check(name, getattr(self, name))
            except FieldError as err:
                errors.append(err)
        if errors:
            raise ExceptionGroup(f"{type(self).__name__} has {len(errors)} invalid field(s)", errors)
        for name, value in cleaned.items():
            setattr(self, name, value)
        return self

    def to_dict(self):
        return {name: getattr(self, name) for name in self.fields()}
