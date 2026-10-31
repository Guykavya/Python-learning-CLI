class ToDictMixin:
    def to_dict(self):
        # TODO: a NEW dict of vars(self), without names that start with "_"
        raise NotImplementedError


class Student:
    # TODO: mix in ToDictMixin; store name, roll and an internal _notes list
    pass


class Product:
    # TODO: mix in ToDictMixin; store sku, price and an internal _discount = 0
    pass
