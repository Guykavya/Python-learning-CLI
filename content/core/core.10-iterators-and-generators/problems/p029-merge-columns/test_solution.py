from solution import csv_lines

NAMES = ["Ann", "Bob", "Cy"]
MARKS = [90, 85]
GRADES = ["A"]


def test_basic():
    assert list(csv_lines([NAMES, MARKS, GRADES], fill="-")) == ["Ann,90,A", "Bob,85,-", "Cy,-,-"], "Go to the LONGEST column and fill the gaps: zip_longest(*columns, fillvalue=fill)."


def test_default_fill():
    assert list(csv_lines([NAMES, MARKS])) == ["Ann,90", "Bob,85", "Cy,"], "The default fill is the empty string."


def test_longest_not_first():
    assert list(csv_lines([["x"], [1, 2, 3]], fill="?")) == ["x,1", "?,2", "?,3"], "The longest column can be any column, not only the first."


def test_numbers_become_text():
    assert list(csv_lines([[1.5], [None]])) == ["1.5,None"], "Turn every value into str before joining."


def test_no_columns():
    assert list(csv_lines([])) == [], "No columns, no lines."


def test_generator_columns():
    names = (n for n in ["a", "b"])
    marks = (m for m in [1, 2, 3])
    assert list(csv_lines([names, marks], fill="0")) == ["a,1", "b,2", "0,3"], "Columns can be generators: do not use len() or indexing on them."


def test_is_generator():
    result = csv_lines([NAMES])
    assert iter(result) is result, "csv_lines must be a generator function (use yield)."
