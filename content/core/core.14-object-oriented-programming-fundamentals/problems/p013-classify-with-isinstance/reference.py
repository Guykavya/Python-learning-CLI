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
    if isinstance(item, ElectricCar):
        return "electric"
    if isinstance(item, Car):
        return "car"
    if isinstance(item, Truck):
        return "truck"
    if isinstance(item, Vehicle):
        return "other vehicle"
    return "not a vehicle"


def count_by_category(items):
    counts = {name: 0 for name in CATEGORIES}
    for item in items:
        counts[category_of(item)] += 1
    return counts
