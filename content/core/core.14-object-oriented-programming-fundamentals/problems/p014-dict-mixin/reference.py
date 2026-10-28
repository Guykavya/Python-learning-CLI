class ToDictMixin:
    def to_dict(self):
        return {name: value for name, value in vars(self).items() if not name.startswith("_")}


class Student(ToDictMixin):
    def __init__(self, name, roll):
        self.name = name
        self.roll = roll
        self._notes = []


class Product(ToDictMixin):
    def __init__(self, sku, price):
        self.sku = sku
        self.price = price
        self._discount = 0
