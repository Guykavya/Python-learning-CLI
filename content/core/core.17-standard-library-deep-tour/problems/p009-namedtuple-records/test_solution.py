import pytest

from solution import Employee, dept_totals, give_raise, parse_rows, to_dicts


def test_employee_type():
    assert Employee is not None, "Define Employee = namedtuple('Employee', [...])."
    assert Employee._fields == ("name", "dept", "salary"), "The fields are name, dept, salary, in that order."
    e = Employee("Asha", "eng", 5)
    assert isinstance(e, tuple), "A namedtuple instance is a real tuple."
    assert e.salary == 5 and e[2] == 5, "Fields work by name and by position."
    assert Employee("Cy", "eng").salary == 0, "salary must default to 0: namedtuple(..., defaults=[0])."
    with pytest.raises(AttributeError):
        e.salary = 9


def test_parse_rows():
    rows = [["Asha", "eng", "50000"], [" Ben ", " ops", " 40000 "], ["Cy", "eng"]]
    got = parse_rows(rows)
    assert got[0] == Employee("Asha", "eng", 50000), "Convert salary to int."
    assert got[1] == Employee("Ben", "ops", 40000), "Strip spaces from every cell, including the salary before int()."
    assert got[2] == Employee("Cy", "eng", 0), "A row with two cells uses the default salary 0."
    assert all(type(e) is Employee for e in got), "Return Employee objects, not plain tuples or lists."


def test_parse_rows_skips_empty():
    got = parse_rows([[], ["A", "x", "1"], []])
    assert got == [Employee("A", "x", 1)], "Skip completely empty rows (csv.reader gives [] for a blank line)."
    assert parse_rows([]) == [], "No rows, no employees."


def test_give_raise_new_object():
    e = Employee("Asha", "eng", 50000)
    r = give_raise(e, 10)
    assert r == Employee("Asha", "eng", 55000), "10% of 50000 is 5000: salary + salary * percent // 100."
    assert e.salary == 50000, "The original must not change. Use _replace, which returns a new tuple."
    assert type(r) is Employee, "_replace returns the same namedtuple type."


def test_give_raise_integer_math():
    assert give_raise(Employee("B", "x", 999), 10).salary == 1098, "999 * 10 // 100 is 99, so 999 + 99 = 1098. Use integer //, not float."
    assert give_raise(Employee("B", "x", 100), 0).salary == 100, "0% leaves the salary as it is."


def test_dept_totals():
    emps = [Employee("A", "ops", 10), Employee("B", "eng", 5), Employee("C", "ops", 1), Employee("D", "hr")]
    got = dept_totals(emps)
    assert got == {"ops": 11, "eng": 5, "hr": 0}, "Add salaries per department; a default-salary person adds 0 but the dept still appears."
    assert list(got) == ["ops", "eng", "hr"], "Departments in first-seen order."
    assert type(got) is dict, "Return a plain dict."


def test_to_dicts():
    got = to_dicts([Employee("Asha", "eng", 1), Employee("Ben", "ops")])
    assert got == [{"name": "Asha", "dept": "eng", "salary": 1}, {"name": "Ben", "dept": "ops", "salary": 0}], "Use _asdict() for each employee."
    assert list(got[0]) == ["name", "dept", "salary"], "Keys in field order."
    assert type(got[0]) is dict, "Each item is a plain dict."


def test_unpack_and_sort():
    emps = parse_rows([["Zed", "a", "3"], ["Amy", "b", "3"], ["Bo", "c", "1"]])
    name, dept, salary = emps[2]
    assert (name, dept, salary) == ("Bo", "c", 1), "A namedtuple unpacks like a tuple."
    assert [e.name for e in sorted(emps, key=lambda e: (e.salary, e.name))] == ["Bo", "Amy", "Zed"], "Sorting with a key over fields works as usual."
