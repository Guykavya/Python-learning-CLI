import ast
import dataclasses
from pathlib import Path

import solution
from solution import Book, Shelf

TREE = ast.parse(Path(solution.__file__).read_text())


def _class(name):
    for node in ast.walk(TREE):
        if isinstance(node, ast.ClassDef) and node.name == name:
            return node
    raise AssertionError(f"class {name} is missing")


def _raises(exc, fn, message):
    try:
        fn()
    except exc:
        return
    except Exception as other:
        raise AssertionError(f"{message} (got {type(other).__name__} instead of {exc.__name__})")
    raise AssertionError(message)


def test_fields_and_describe():
    b = Book("Dune", "Herbert", 1965)
    assert (b.title, b.author, b.year) == ("Dune", "Herbert", 1965), "Book fields in order: title, author, year."
    assert b.describe() == "Dune by Herbert (1965)", "describe() returns 'Title by Author (year)'."
    assert Book("A", "B", 1450).year == 1450 and Book("A", "B", 2100).year == 2100, "1450 and 2100 are valid years."


def test_equality_and_hash():
    a, b = Book("Dune", "Herbert", 1965), Book("Dune", "Herbert", 1965)
    assert a == b, "Two books with the same fields are equal (a dataclass gives __eq__)."
    assert Book("Dune", "Herbert", 1965) != Book("Dune", "Herbert", 1966), "A different year is a different book."
    assert len({a, b}) == 1, "Books must be hashable and equal books hash the same: use frozen=True."


def test_frozen():
    b = Book("Dune", "Herbert", 1965)
    _raises(dataclasses.FrozenInstanceError, lambda: setattr(b, "year", 2000),
            "Changing a field must raise FrozenInstanceError: use @dataclass(frozen=True).")


def test_validation():
    _raises(ValueError, lambda: Book("", "x", 2000), "An empty title must raise ValueError in __post_init__.")
    _raises(ValueError, lambda: Book("T", "x", 1449), "Year 1449 is too early: ValueError.")
    _raises(ValueError, lambda: Book("T", "x", 2101), "Year 2101 is too late: ValueError.")


def test_order():
    books = [Book("B", "z", 2000), Book("A", "z", 2001), Book("A", "y", 2005), Book("A", "y", 1999)]
    assert sorted(books) == [Book("A", "y", 1999), Book("A", "y", 2005), Book("A", "z", 2001), Book("B", "z", 2000)], (
        "Books sort by title, then author, then year: use order=True."
    )
    assert Book("A", "a", 2000) < Book("B", "a", 1900), "'<' compares fields in order (title first)."


def test_replace():
    b = Book("Dune", "Herbert", 1965)
    c = dataclasses.replace(b, year=1966)
    assert c == Book("Dune", "Herbert", 1966), "replace() makes a copy with one field changed."
    assert b.year == 1965, "The original book is unchanged."
    _raises(ValueError, lambda: dataclasses.replace(b, year=5), "replace() runs __post_init__, so bad data is rejected.")


def test_repr():
    assert repr(Book("T", "A", 1999)) == "Book(title='T', author='A', year=1999)", "Let the dataclass write __repr__."


def test_shelf():
    s = Shelf("fiction")
    assert s.name == "fiction" and s.books == [], "A new shelf has a name and an empty list of books."
    s.add(Book("B", "x", 2000))
    s.add(Book("A", "x", 2000))
    assert s.titles() == ["B", "A"], "titles() keeps insertion order."
    assert [b.title for b in s.sorted_books()] == ["A", "B"], "sorted_books() uses the Book ordering."
    assert [b.title for b in s.books] == ["B", "A"], "sorted_books() must not reorder the shelf itself."


def test_shelves_do_not_share_books():
    s1, s2 = Shelf("one"), Shelf("two")
    s1.add(Book("A", "x", 2000))
    assert s2.books == [], "Two shelves share one list. Use field(default_factory=list), not books = []."
    assert Shelf("x") == Shelf("x"), "Dataclass equality works for shelves too."


def test_structure():
    for name in ("Book", "Shelf"):
        decos = _class(name).decorator_list
        assert decos, f"{name} must be decorated with @dataclass."
    book_deco = _class("Book").decorator_list[0]
    kws = {k.arg: k.value.value for k in getattr(book_deco, "keywords", []) if isinstance(k.value, ast.Constant)}
    assert kws.get("frozen") is True and kws.get("order") is True, "Book: @dataclass(frozen=True, order=True)."
    methods = {n.name for n in _class("Book").body if isinstance(n, ast.FunctionDef)}
    assert "__post_init__" in methods, "Book needs __post_init__ for the validation."
    handwritten = methods & {"__eq__", "__hash__", "__repr__", "__lt__", "__init__", "__le__", "__gt__", "__ge__"}
    assert not handwritten, f"Do not write {sorted(handwritten)} by hand: the dataclass makes them."
    assert any(isinstance(n, ast.Name) and n.id == "field" or isinstance(n, ast.Attribute) and n.attr == "field"
               for n in ast.walk(_class("Shelf"))), "Shelf: use field(default_factory=list) for the books."
    assert not any(isinstance(n, ast.Dict) for n in ast.walk(TREE)), "No dict literals are needed any more: the record is a class."
