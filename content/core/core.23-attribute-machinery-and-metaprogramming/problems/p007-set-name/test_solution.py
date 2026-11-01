import pytest

from solution import Field


class Book:
    title = Field()
    pages = Field(default=0)

    def __init__(self, title=None):
        if title is not None:
            self.title = title


def test_field_learns_its_name():
    assert Book.title.name == "title", "__set_name__(owner, name) runs when the class is created: store the name."
    assert Book.pages.name == "pages", "Each Field gets its own name, even though both are Field objects."


def test_class_access_returns_descriptor():
    assert isinstance(Book.title, Field), "Book.title (instance is None) must return the Field itself."


def test_unset_field_gives_default():
    b = Book()
    assert b.title is None, "A field with no default returns None until it is set."
    assert b.pages == 0, "Field(default=0) returns 0 until it is set."


def test_value_is_stored_in_instance_dict_under_field_name():
    b = Book("Dune")
    assert b.title == "Dune", "Reading the field must give back the value you set."
    assert vars(b) == {"title": "Dune"}, (
        "Store the value in instance.__dict__ under the field's own name (vars(b) should be {'title': 'Dune'}). "
        "Unset fields store nothing."
    )


def test_values_are_not_shared_between_instances():
    a = Book("Dune")
    b = Book("Emma")
    a.pages = 412
    assert (a.title, b.title) == ("Dune", "Emma"), (
        "Each book keeps its own title. Storing the value on the descriptor (self.value) shares it between ALL books."
    )
    assert b.pages == 0, "Setting a.pages must not change b.pages."


def test_assignment_updates_the_stored_value():
    b = Book("Dune")
    b.title = "Emma"
    assert b.title == "Emma" and vars(b)["title"] == "Emma", "Assignment goes through __set__ and updates the stored value."


def test_delete_returns_to_default():
    b = Book("Dune")
    del b.title
    assert b.title is None, "After del, the field shows its default again."
    assert "title" not in vars(b), "del must remove the value from the instance dict."


def test_delete_unset_field_raises_attribute_error():
    b = Book()
    with pytest.raises(AttributeError) as info:
        del b.pages
    assert "pages" in str(info.value), "Deleting a field that was never set raises AttributeError naming the field (not KeyError)."


def test_works_in_any_class():
    class User:
        email = Field(default="")

    u = User()
    u.email = "a@b.c"
    assert (User.email.name, u.email, vars(u)) == ("email", "a@b.c", {"email": "a@b.c"}), (
        "Nothing may be hard-coded: the same Field class must work for any attribute name in any class."
    )
