class Value:
    def __init__(self, value):
        # TODO: store value through the property
        pass

    # TODO: a property `value` with a validating setter (self._value holds the number)


class BoundedValue(Value):
    def __init__(self, value, upper):
        # TODO: check and store upper, then let Value.__init__ store the value
        pass

    # TODO: override the property: keep the getter, add the upper check, reuse Value's setter
