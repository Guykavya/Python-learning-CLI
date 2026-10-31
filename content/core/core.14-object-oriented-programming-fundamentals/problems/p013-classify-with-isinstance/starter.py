class Vehicle:
    def __init__(self, plate):
        self.plate = plate


class Car(Vehicle):
    pass


class ElectricCar(Car):
    pass


class Truck(Vehicle):
    pass


CATEGORIES = ["electric", "car", "truck", "other vehicle", "not a vehicle"]


def category_of(item):
    # TODO: most specific class first
    return "not a vehicle"


def count_by_category(items):
    # TODO: a dict with all five categories
    return {}
