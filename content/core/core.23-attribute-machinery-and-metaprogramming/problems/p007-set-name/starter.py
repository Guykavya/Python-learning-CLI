class Field:
    def __init__(self, default=None):
        self.default = default
        self.value = default

    # TODO: __set_name__ so the field learns its attribute name

    def __get__(self, instance, owner=None):
        return self.value  # BUG: one value shared by every instance

    def __set__(self, instance, value):
        self.value = value

    # TODO: __delete__
