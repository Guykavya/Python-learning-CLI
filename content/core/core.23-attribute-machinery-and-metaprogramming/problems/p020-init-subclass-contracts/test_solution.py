import pytest

from solution import Record


def test_valid_subclass_and_instances():
    class User(Record):
        table = "users"
        fields = ("id", "name")

    u = User(name="Ann", id=1)
    assert (u.id, u.name) == (1, "Ann"), "__init__ must store each field as an instance attribute."
    assert repr(u) == "User(id=1, name='Ann')", (
        f"repr must list the fields in `fields` order with repr() of each value, got {repr(u)!r}."
    )


def test_missing_both_attributes_fails_at_class_creation():
    with pytest.raises(TypeError) as err:
        class Broken(Record):
            pass
    msg = str(err.value)
    assert "Broken" in msg, f"The message must name the class. Got {msg!r}"
    assert "fields" in msg and "table" in msg, f"The message must list EVERY missing attribute. Got {msg!r}"


def test_missing_one_attribute():
    with pytest.raises(TypeError) as err:
        class NoColumns(Record):
            table = "things"
    assert "fields" in str(err.value), f"'fields' is missing and must be named. Got {str(err.value)!r}"


@pytest.mark.parametrize(
    "table, fields, why",
    [
        ("", ("a",), "table must not be empty"),
        (5, ("a",), "table must be a str"),
        ("t", ["a", "b"], "fields must be a tuple, not a list"),
        ("t", (), "fields must not be empty"),
        ("t", ("a", 1), "every field name must be a str"),
        ("t", ("a", "b", "a"), "field names must be unique"),
    ],
)
def test_bad_values_fail_at_class_creation(table, fields, why):
    with pytest.raises(TypeError):
        type("Bad", (Record,), {"table": table, "fields": fields})
        pytest.fail(f"Class creation must raise TypeError because {why}.")


def test_inherited_attributes_satisfy_the_contract():
    class User(Record):
        table = "users"
        fields = ("id", "name")

    class Admin(User):
        pass

    a = Admin(id=1, name="root")
    assert repr(a) == "Admin(id=1, name='root')", (
        "A subclass may inherit table and fields (use hasattr/getattr, not cls.__dict__); repr uses the real class name."
    )


def test_abstract_skips_the_check_but_is_not_inherited():
    class Timestamped(Record, abstract=True):
        pass

    class Event(Timestamped):
        table = "events"
        fields = ("at", "what")

    assert repr(Event(at=1, what="x")) == "Event(at=1, what='x')"
    with pytest.raises(TypeError):
        class Forgot(Timestamped):
            pass


def test_cooperates_with_other_init_subclass():
    class Tagged:
        def __init_subclass__(cls, /, tag=None, **kwargs):
            super().__init_subclass__(**kwargs)
            cls.tag = tag

    class User(Record, Tagged, tag="people"):
        table = "users"
        fields = ("id",)

    assert User.tag == "people", (
        "Record.__init_subclass__ must pass unknown keywords on with super().__init_subclass__(**kwargs), "
        "so the next class in the MRO (Tagged) receives tag=..."
    )


def test_unknown_class_keyword_is_still_an_error():
    with pytest.raises(TypeError):
        class Odd(Record, colour="red"):
            table = "odd"
            fields = ("id",)


def test_init_requires_exactly_the_fields():
    class User(Record):
        table = "users"
        fields = ("id", "name")

    with pytest.raises(TypeError) as err:
        User(id=1)
    assert "name" in str(err.value), "A missing field must be named in the TypeError."
    with pytest.raises(TypeError) as err:
        User(id=1, name="Ann", age=3)
    assert "age" in str(err.value), "An unknown field must be named in the TypeError."


def test_own_repr_is_kept():
    class Secret(Record):
        table = "secrets"
        fields = ("key",)

        def __repr__(self):
            return "Secret(***)"

    assert repr(Secret(key="abc")) == "Secret(***)", (
        "A subclass that defines its own __repr__ must keep it. Do not overwrite cls.__repr__ unconditionally."
    )
