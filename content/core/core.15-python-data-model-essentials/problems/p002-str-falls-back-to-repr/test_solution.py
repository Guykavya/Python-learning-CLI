from solution import Book, Tag


def test_book_repr():
    b = Book("Dune", "Frank Herbert")
    assert repr(b) == "Book('Dune', 'Frank Herbert')", "Book.__repr__ should look like code: Book('Dune', 'Frank Herbert'). Use !r on the values."


def test_book_str():
    b = Book("Dune", "Frank Herbert")
    assert str(b) == "Dune by Frank Herbert", "Book.__str__ should be friendly text: 'Dune by Frank Herbert'."


def test_print_uses_str(capsys):
    print(Book("Dune", "Frank Herbert"))
    assert capsys.readouterr().out == "Dune by Frank Herbert\n", "print() calls __str__."


def test_list_uses_repr():
    b = Book("Dune", "Frank Herbert")
    assert str([b]) == "[Book('Dune', 'Frank Herbert')]", "A list shows its items with repr(), so this needs __repr__, not __str__."


def test_tag_repr():
    assert repr(Tag("python")) == "Tag('python')", "Tag.__repr__ should be Tag('python')."


def test_tag_str_falls_back():
    assert str(Tag("python")) == "Tag('python')", "str() falls back to __repr__ when __str__ is not defined."


def test_tag_has_no_own_str():
    assert "__str__" not in Tag.__dict__, "Do not define __str__ on Tag. The point is that __repr__ alone is enough."
