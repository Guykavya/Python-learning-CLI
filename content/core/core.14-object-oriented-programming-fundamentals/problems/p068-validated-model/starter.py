class FieldError(Exception):
    # TODO
    pass


class Field:
    def __init__(self, *, required=True, default=None):
        # TODO
        pass

    def check(self, name, value):
        # TODO
        return value


class IntField(Field):
    # TODO
    pass


class StrField(Field):
    # TODO
    pass


class Model:
    # TODO: fields (classmethod), __init__, validate, to_dict
    pass
