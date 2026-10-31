import pytest

from solution import Employee, Manager, Person


def test_hierarchy():
    assert issubclass(Employee, Person), "Employee must inherit from Person."
    assert issubclass(Manager, Employee), "Manager must inherit from Employee."


def test_person():
    p = Person("Asha", 34)
    assert (p.name, p.age) == ("Asha", 34), "Person stores name and age."
    assert p.describe() == "Asha (34)", "Person.describe() should return 'Asha (34)'."


def test_employee_has_parent_fields():
    e = Employee("Ravi", 28, "E7", 50000)
    assert hasattr(e, "name") and hasattr(e, "age"), (
        "An Employee has no name/age. Call super().__init__(name, age) in Employee.__init__."
    )
    assert (e.name, e.age, e.employee_id, e.salary) == ("Ravi", 28, "E7", 50000), "Employee stores all four fields."


def test_manager_has_all_fields():
    m = Manager("Asha", 34, "M1", 90000)
    assert hasattr(m, "employee_id") and hasattr(m, "name"), (
        "A Manager is missing parent fields. Call super().__init__(name, age, employee_id, salary) in Manager.__init__."
    )
    assert (m.name, m.age, m.employee_id, m.salary) == ("Asha", 34, "M1", 90000), "Manager stores all fields through the chain."
    assert m.reports == [], "A new Manager starts with an empty reports list."


def test_age_check_runs_from_every_level():
    for make in (lambda: Person("X", -1), lambda: Employee("X", -1, "E1", 10), lambda: Manager("X", -1, "M1", 10)):
        try:
            make()
        except ValueError as e:
            assert "age cannot be negative" in str(e), "Use the message 'age cannot be negative'."
        else:
            pytest.fail(
                "A negative age must raise ValueError at every level. Do not set self.age yourself in a subclass; "
                "call super().__init__ so Person's check runs."
            )


def test_salary_check_runs_for_managers_too():
    with pytest.raises(ValueError, match="salary cannot be negative"):
        Employee("X", 30, "E1", -5)
    with pytest.raises(ValueError, match="salary cannot be negative"):
        Manager("X", 30, "M1", -5)


def test_describe_chain():
    e = Employee("Ravi", 28, "E7", 50000)
    assert e.describe() == "Ravi (28), id E7", "Employee.describe() = parent text + ', id E7'. Use super().describe()."
    m = Manager("Asha", 34, "M1", 90000)
    assert m.describe() == "Asha (34), id M1, 0 reports", "Manager.describe() = Employee text + ', 0 reports'."


def test_describe_uses_super_not_a_copy():
    original = Person.describe
    try:
        Person.describe = lambda self: f"<{self.name}>"
        m = Manager("Asha", 34, "M1", 90000)
        assert m.describe() == "<Asha>, id M1, 0 reports", (
            "When Person.describe changes, Employee and Manager should follow. Build on super().describe() "
            "instead of repeating the name/age format."
        )
    finally:
        Person.describe = original


def test_add_report():
    m = Manager("Asha", 34, "M1", 90000)
    r = Employee("Ravi", 28, "E7", 50000)
    n = Employee("Neha", 25, "E8", 45000)
    m.add_report(r)
    m.add_report(n)
    assert len(m.reports) == 2 and m.reports[0] is r and m.reports[1] is n, "add_report appends the employee objects in order."
    assert m.describe() == "Asha (34), id M1, 2 reports", "describe() should count the reports."


def test_manager_can_report_to_manager():
    boss = Manager("Big", 50, "M0", 200000)
    mid = Manager("Asha", 34, "M1", 90000)
    boss.add_report(mid)
    assert boss.reports[0] is mid, "A Manager is an Employee, so a manager can report to another manager."


def test_each_manager_has_own_reports_list():
    a = Manager("A", 40, "M1", 1)
    b = Manager("B", 41, "M2", 1)
    a.add_report(Employee("Ravi", 28, "E7", 50000))
    assert b.reports == [], "Each manager needs its own list. Create self.reports = [] in __init__, not as a class attribute."


def test_add_report_rejects_non_employees():
    m = Manager("Asha", 34, "M1", 90000)
    for bad in ("Ravi", Person("Kid", 10), 42):
        with pytest.raises(TypeError, match="reports must be employees"):
            m.add_report(bad)
    assert m.reports == [], "Rejected values must not be added."


def test_add_report_rejects_self():
    m = Manager("Asha", 34, "M1", 90000)
    with pytest.raises(ValueError, match="a manager cannot report to themselves"):
        m.add_report(m)
    assert m.reports == [], "The manager must not be added to their own reports."
