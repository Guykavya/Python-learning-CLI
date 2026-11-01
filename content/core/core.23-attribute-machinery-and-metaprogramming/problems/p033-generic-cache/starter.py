import types


class Box:
    item_type = object

    def __init__(self):
        self._value = None

    def put(self, value):
        self._value = value

    def get(self):
        return self._value

    def __class_getitem__(cls, param):
        return cls
