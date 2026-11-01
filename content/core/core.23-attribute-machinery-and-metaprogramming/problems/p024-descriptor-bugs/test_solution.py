import copy
import re

import pytest

from solution import Alias, Field, Model


class Product(Model):
    name = Field(str)
    price = Field(float, default=0.0)
    cost = Alias("price")


class Point(Model):
    x = Field(int)
    y = Field(int)


def test_bug1_values_are_per_instance():
    a = Product(name="pen", price=1.5)
    b = Product(name="ink", price=9.0)
    assert a.name == "pen" and a.price == 1.5, (
        f"a.name is {a.name!r} after creating b. Bug 1: Field stores the value on the descriptor "
        "(self.value), and one descriptor serves EVERY instance. Store it in instance.__dict__ instead."
    )
    assert b.name == "ink"


def test_bug1_two_fields_in_one_object_are_separate():
    p = Point(x=1, y=2)
    assert (p.x, p.y) == (1, 2), (
        "x and y share one storage slot. Each field must store under its own name (learned in __set_name__)."
    )


def test_bug1_default_is_per_instance():
    a = Product(name="a")
    b = Product(name="b", price=5.0)
    assert a.price == 0.0, "a never set price, so it must get the default 0.0 even after b set its own price."
    assert b.price == 5.0


def test_unset_field_without_default_raises_attribute_error():
    p = Point(x=1)
    with pytest.raises(AttributeError):
        p.y
    assert not hasattr(p, "y"), "An unset field with no default must look missing (AttributeError)."


def test_bug2_error_message_names_the_field():
    with pytest.raises(TypeError) as err:
        Product(name="pen", price=2)
    msg = str(err.value)
    assert re.search(r"\bprice\b", msg), (
        f"Message was {msg!r}. Bug 2: the Field never learns its attribute name. Add __set_name__(self, owner, name)."
    )
    with pytest.raises(TypeError) as err:
        Point(x="1")
    assert re.search(r"\bx\b", str(err.value)), f"The message for x must name 'x', got {str(err.value)!r}"


def test_bug2_field_knows_its_name():
    assert Product.__dict__["price"].name == "price", "Field.name must be the attribute name, set by __set_name__."
    assert Point.__dict__["y"].name == "y"


def test_type_check_still_works_and_keeps_old_value():
    p = Product(name="pen", price=1.5)
    with pytest.raises(TypeError):
        p.price = "free"
    assert p.price == 1.5, "A rejected value must not replace the stored one."


def test_bug3_class_access_returns_descriptors():
    try:
        alias = Product.cost
    except AttributeError:
        pytest.fail(
            "Product.cost crashed. Bug 3: on class access __get__ receives instance=None, and Alias.__get__ "
            "calls getattr(None, 'price'). Return self when instance is None."
        )
    assert isinstance(alias, Alias), "Product.cost must return the Alias object itself."
    assert isinstance(Product.price, Field), "Product.price must return the Field object itself."


def test_alias_reads_and_writes_the_target():
    p = Product(name="pen", price=1.5)
    assert p.cost == 1.5, "p.cost reads p.price."
    p.cost = 2.5
    assert p.price == 2.5, "p.cost = 2.5 writes p.price."
    with pytest.raises(TypeError):
        p.cost = 3


def test_extras_are_readable():
    p = Product(name="pen", colour="blue")
    assert p.colour == "blue", "Keywords that are not fields go to extras and are readable as attributes."
    with pytest.raises(AttributeError) as err:
        p.weight
    assert "weight" in str(err.value), "A missing extra raises AttributeError naming it."


def test_bug4_copy_does_not_recurse():
    p = Product(name="pen", price=1.5, colour="blue")
    try:
        clone = copy.copy(p)
    except RecursionError:
        pytest.fail(
            "copy.copy hit RecursionError. Bug 4: copy builds the new object WITHOUT __init__, so 'extras' is "
            "missing; self.extras inside __getattr__ then calls __getattr__('extras') again, forever. "
            "Read it with vars(self).get('extras', {}) or object.__getattribute__."
        )
    assert clone.colour == "blue", "The copy keeps the extras."


def test_bug4_blank_object_answers_hasattr():
    blank = Product.__new__(Product)
    try:
        result = hasattr(blank, "colour")
    except RecursionError:
        pytest.fail("hasattr on an object whose __init__ never ran must return False, not recurse (bug 4).")
    except KeyError:
        pytest.fail("Missing names must raise AttributeError, not KeyError: hasattr only understands AttributeError.")
    assert result is False
