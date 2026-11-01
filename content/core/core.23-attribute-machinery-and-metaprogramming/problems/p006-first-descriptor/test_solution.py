import pytest

from solution import Fahrenheit, Upper


class Person:
    shout = Upper("name")
    loud_city = Upper("city")

    def __init__(self, name, city):
        self.name = name
        self.city = city


class Temperature:
    fahrenheit = Fahrenheit()

    def __init__(self, celsius):
        self.celsius = celsius


def test_upper_reads_the_source_attribute():
    p = Person("ada", "london")
    assert p.shout == "ADA", "Upper('name').__get__ must return instance.name in upper case."
    assert p.loud_city == "LONDON", "Each Upper reads the attribute named by ITS source, not always 'name'."


def test_upper_follows_changes():
    p = Person("ada", "london")
    p.name = "grace"
    assert p.shout == "GRACE", "The value is computed on every read; do not cache the first result."


def test_upper_values_are_per_instance():
    a, b = Person("ada", "x"), Person("bob", "y")
    assert (a.shout, b.shout) == ("ADA", "BOB"), (
        "One descriptor object serves every Person. Read from the instance passed to __get__, never store it on self."
    )


def test_class_access_returns_the_descriptor():
    assert Person.shout is Person.__dict__["shout"], (
        "Person.shout calls __get__(None, Person). When instance is None, return the descriptor itself (self)."
    )
    assert isinstance(Person.shout, Upper)


def test_upper_is_non_data_so_instance_can_shadow_it():
    p = Person("ada", "london")
    p.shout = "custom"
    assert p.shout == "custom", (
        "Upper must be a NON-data descriptor (only __get__), so an instance attribute with the same name wins."
    )
    del p.shout
    assert p.shout == "ADA", "After deleting the instance attribute the descriptor works again."


def test_fahrenheit_reads():
    assert Temperature(100).fahrenheit == pytest.approx(212), "100 C is 212 F (C * 9 / 5 + 32)."
    assert Temperature(-40).fahrenheit == pytest.approx(-40), "-40 C is -40 F."


def test_fahrenheit_writes_celsius():
    t = Temperature(0)
    t.fahrenheit = 212
    assert t.celsius == pytest.approx(100), "Setting fahrenheit must update celsius: (F - 32) * 5 / 9."
    assert t.fahrenheit == pytest.approx(212), "Reading back must give the value you set."


def test_fahrenheit_stores_nothing_of_its_own():
    t = Temperature(10)
    t.fahrenheit = 50
    assert "fahrenheit" not in vars(t), (
        "Fahrenheit must be a DATA descriptor (define __set__): the assignment must go to __set__, not into the instance dict."
    )
    assert vars(t) == {"celsius": pytest.approx(10)}, "Only celsius is stored; fahrenheit is always computed from it."


def test_fahrenheit_instances_independent():
    a, b = Temperature(0), Temperature(100)
    a.fahrenheit = 50
    assert b.celsius == 100, "Setting a.fahrenheit must not touch b. Do not store the value on the descriptor."


def test_fahrenheit_class_access():
    assert isinstance(Temperature.fahrenheit, Fahrenheit), "Temperature.fahrenheit must return the descriptor (instance is None)."
