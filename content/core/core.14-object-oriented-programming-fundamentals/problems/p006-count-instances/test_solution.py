import pytest

from solution import Ticket


@pytest.fixture(autouse=True)
def fresh_counter():
    Ticket.count = 0
    yield


def test_count_starts_at_zero_in_class_body():
    assert "count" in vars(Ticket), "Put count = 0 directly in the class body, so it is a class attribute."


def test_numbers_increase():
    a = Ticket("Printer jam")
    b = Ticket("No wifi")
    c = Ticket("Slow laptop")
    assert a.title == "Printer jam", "Store the title on self."
    assert (a.number, b.number, c.number) == (1, 2, 3), (
        "Tickets should be numbered 1, 2, 3. If all are 1, you wrote self.count += 1, which makes an "
        "instance attribute and never changes the class counter."
    )


def test_class_counter_changes():
    Ticket("x")
    Ticket("y")
    assert Ticket.count == 2, "After two tickets, Ticket.count must be 2. Change the class attribute (Ticket.count += 1), not self.count."


def test_number_is_stored_on_the_instance():
    a = Ticket("x")
    Ticket("y")
    assert a.number == 1, "Each ticket keeps its own number. Store it with self.number = ..., do not read the class counter later."
    assert "number" in vars(a), "number should be an instance attribute (self.number)."
    assert "count" not in vars(a), "The ticket should not get its own 'count'. That happens with self.count += 1."


def test_how_many():
    assert Ticket.how_many() == 0, "how_many() should return 0 before any ticket is made."
    Ticket("x")
    assert Ticket.how_many() == 1, "how_many() should return the class counter."


def test_reset_starts_numbers_again():
    a = Ticket("x")
    Ticket("y")
    Ticket.reset()
    assert Ticket.count == 0, "reset() must set the class counter back to 0: cls.count = 0."
    c = Ticket("z")
    assert c.number == 1, "After reset(), the next ticket is number 1."
    assert a.number == 1, "reset() must not change tickets that already exist."


def test_reset_and_how_many_are_classmethods():
    assert isinstance(vars(Ticket)["reset"], classmethod), "Decorate reset with @classmethod, so it receives the class as cls."
    assert isinstance(vars(Ticket)["how_many"], classmethod), "Decorate how_many with @classmethod."


def test_reset_through_an_instance_resets_the_class():
    t = Ticket("x")
    Ticket("y")
    t.reset()
    assert Ticket.count == 0, "A classmethod called on an instance still gets the class as cls, so the class counter resets."
    assert "count" not in vars(t), "reset() must change the class, not create an instance attribute on t."
