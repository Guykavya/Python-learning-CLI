class Field:
    def __init__(self, default=None):
        self.default = default

    def __set_name__(self, owner, name):
        pass

    def __get__(self, obj, owner=None):
        return self.default

    def __set__(self, obj, value):
        pass


class Observable:
    def __init__(self, **values):
        pass


def fields(obj_or_cls):
    return ()


def subscribe(obj, callback):
    return callback


def unsubscribe(obj, callback):
    pass


def history(obj):
    return []


def undo(obj):
    return None
