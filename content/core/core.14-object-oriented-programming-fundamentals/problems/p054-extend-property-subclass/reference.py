def _is_number(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


class Value:
    def __init__(self, value):
        self.value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new):
        if not _is_number(new):
            raise TypeError("value must be a number")
        if new < 0:
            raise ValueError("value must be >= 0")
        self._value = new


class BoundedValue(Value):
    def __init__(self, value, upper):
        if not _is_number(upper) or upper < 0:
            raise ValueError("upper must be a number >= 0")
        self.upper = upper  # must exist before the setter runs
        super().__init__(value)

    @Value.value.setter
    def value(self, new):
        if _is_number(new) and new > self.upper:
            raise ValueError(f"value must be <= {self.upper}")
        Value.value.fset(self, new)
