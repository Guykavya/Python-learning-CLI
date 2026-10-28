from solution import Car, ElectricCar, Truck, Vehicle, category_of, count_by_category


def test_basic_categories():
    assert category_of(Car("A")) == "car", "A Car is in the 'car' category."
    assert category_of(Truck("A")) == "truck", "A Truck is in the 'truck' category."
    assert category_of(Vehicle("A")) == "other vehicle", "A plain Vehicle is 'other vehicle'."


def test_electric_before_car():
    assert category_of(ElectricCar("A")) == "electric", (
        "An ElectricCar is also a Car, so isinstance(x, Car) is True for it. Check ElectricCar BEFORE Car."
    )


def test_not_a_vehicle():
    for thing in ("bike", 42, None, [Car("A")]):
        assert category_of(thing) == "not a vehicle", f"{thing!r} is not a Vehicle, so it is 'not a vehicle'."


def test_subclasses_defined_later():
    class SportsCar(Car):
        pass

    class Tesla(ElectricCar):
        pass

    class Bus(Vehicle):
        pass

    assert category_of(SportsCar("S")) == "car", "A subclass of Car counts as 'car'. Use isinstance, not type(x) == Car."
    assert category_of(Tesla("T")) == "electric", "A subclass of ElectricCar counts as 'electric'."
    assert category_of(Bus("B")) == "other vehicle", "A Bus is a Vehicle but not a Car or Truck: 'other vehicle'."


def test_count_example():
    items = [Car("KA01"), ElectricCar("KA02"), Truck("KA03"), Vehicle("KA04"), "bike", ElectricCar("KA05")]
    assert count_by_category(items) == {
        "electric": 2, "car": 1, "truck": 1, "other vehicle": 1, "not a vehicle": 1,
    }, "Count each item once, in its most specific category."


def test_count_has_all_keys_in_order():
    result = count_by_category([Truck("X")])
    assert list(result) == ["electric", "car", "truck", "other vehicle", "not a vehicle"], (
        "The dict must contain all five categories, in the order given, even when a count is 0."
    )
    assert result["truck"] == 1 and result["car"] == 0, "Only the truck is counted."


def test_count_empty():
    assert count_by_category([]) == {
        "electric": 0, "car": 0, "truck": 0, "other vehicle": 0, "not a vehicle": 0,
    }, "With no items, every count is 0."


def test_each_item_counted_once():
    result = count_by_category([ElectricCar("E")])
    assert sum(result.values()) == 1, "An ElectricCar must be counted once, not as electric AND car AND vehicle. Use if/return or elif."
