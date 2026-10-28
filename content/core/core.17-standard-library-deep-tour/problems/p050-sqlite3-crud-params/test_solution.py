import sqlite3

import pytest

from solution import ContactBook


@pytest.fixture
def book():
    b = ContactBook()
    try:
        yield b
    finally:
        b.close()


def test_add_returns_ids(book):
    assert book.add("Asha", "asha@example.com", "Pune") == 1, "The first row of an INTEGER PRIMARY KEY gets id 1: return cursor.lastrowid."
    assert book.add("Ravi", "ravi@example.com") == 2, "The next insert gets id 2."
    assert book.count() == 2, "count() is SELECT COUNT(*): two contacts were added."


def test_get(book):
    i = book.add("Asha", "asha@example.com", "Pune")
    assert book.get(i) == {"id": i, "name": "Asha", "email": "asha@example.com", "city": "Pune"}, (
        "get returns a dict with id, name, email, city: set conn.row_factory = sqlite3.Row and use dict(row)."
    )
    assert book.get(999) is None, "No such id: fetchone() returns None, and so must get()."
    assert book.get(book.add("NoCity", "n@example.com"))["city"] is None, "A missing city is stored as NULL and comes back as None."


def test_find_by_city_ordered(book):
    book.add("Ravi", "ravi@example.com", "Pune")
    book.add("Asha", "asha@example.com", "Pune")
    book.add("Meera", "meera@example.com", "Delhi")
    names = [c["name"] for c in book.find_by_city("Pune")]
    assert names == ["Asha", "Ravi"], "Only Pune contacts, ordered by name (ORDER BY name)."
    assert book.find_by_city("Agra") == [], "A city with nobody gives an empty list."


def test_duplicate_email_is_value_error(book):
    book.add("Asha", "asha@example.com")
    with pytest.raises(ValueError):
        book.add("Other", "asha@example.com")
    assert book.count() == 1, "The failed insert must not leave a row behind."
    book.add("Ravi", "ravi@example.com")
    assert book.count() == 2, "After a failed insert the book must keep working (roll back the failed transaction)."


def test_update_email(book):
    a = book.add("Asha", "asha@example.com")
    b = book.add("Ravi", "ravi@example.com")
    assert book.update_email(a, "asha@new.example") is True, "One row changed: return True (cursor.rowcount == 1)."
    assert book.get(a)["email"] == "asha@new.example", "The new email must be stored."
    assert book.update_email(999, "x@example.com") is False, "No such id: rowcount is 0, return False."
    with pytest.raises(ValueError):
        book.update_email(b, "asha@new.example")
    assert book.get(b)["email"] == "ravi@example.com", "A refused update leaves the old email."


def test_delete(book):
    a = book.add("Asha", "asha@example.com")
    assert book.delete(a) is True, "Deleting an existing id returns True."
    assert book.delete(a) is False, "Deleting it again changes nothing: False."
    assert book.get(a) is None and book.count() == 0, "The row must be gone."


def test_quotes_and_injection_are_just_data(book):
    i = book.add("O'Brien", "ob@example.com", "St. John's")
    assert book.get(i)["name"] == "O'Brien", "A quote in a value breaks string-built SQL: use ? parameters."
    evil = "x'); DROP TABLE contacts; --"
    j = book.add(evil, "evil@example.com", "Pune")
    assert book.get(j)["name"] == evil, "The value must be stored exactly as given."
    assert book.count() == 2, "The table must still exist: values never become SQL."
    assert book.find_by_city("x' OR '1'='1") == [], "With parameters, ' OR '1'='1 is just a city name that matches nothing."
    assert [c["name"] for c in book.find_by_city("St. John's")] == ["O'Brien"], "A city with a quote must be found too."


def test_data_survives_reopen(tmp_path):
    path = tmp_path / "contacts.db"
    first = ContactBook(str(path))
    try:
        first.add("Asha", "asha@example.com", "Pune")
        first.add("Ravi", "ravi@example.com", "Pune")
        first.update_email(1, "asha@new.example")
        first.delete(2)
    finally:
        first.close()
    second = ContactBook(str(path))
    try:
        assert second.count() == 1, "After closing and reopening, the data must still be there: commit after every change."
        assert second.get(1)["email"] == "asha@new.example", "The update must be committed too."
    finally:
        second.close()


def test_context_manager_closes(tmp_path):
    path = tmp_path / "c.db"
    with ContactBook(str(path)) as book:
        assert isinstance(book, ContactBook), "__enter__ must return the book itself."
        book.add("Asha", "asha@example.com")
    with pytest.raises(sqlite3.ProgrammingError):
        book.count()                       # a closed connection cannot be used
    with ContactBook(str(path)) as again:
        assert again.count() == 1, "Opening the same file again must not wipe the table: CREATE TABLE IF NOT EXISTS."
