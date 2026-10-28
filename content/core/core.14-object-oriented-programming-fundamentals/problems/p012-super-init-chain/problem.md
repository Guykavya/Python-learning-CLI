# A chain of `__init__` methods with `super()`

When a subclass has its own `__init__`, the parent's `__init__` does **not** run by itself. The
subclass must call it with `super().__init__(...)`, then add its own fields. The same works for any
method: `super().describe()` runs the parent's version, and the subclass extends the result.

Write three classes in `solution.py`:

**`Person(name, age)`**
- Stores `name` and `age`. If `age` is negative, raise `ValueError("age cannot be negative")`.
- `describe()` returns `"<name> (<age>)"`, for example `"Asha (34)"`.

**`Employee(name, age, employee_id, salary)`**, a subclass of `Person`
- Calls `super().__init__(name, age)`, then stores `employee_id` and `salary`.
  If `salary` is negative, raise `ValueError("salary cannot be negative")`.
- `describe()` returns the parent's text plus `", id <employee_id>"`: `"Ravi (28), id E7"`.

**`Manager(name, age, employee_id, salary)`**, a subclass of `Employee`
- Calls `super().__init__(...)`, then starts with an empty list `reports`.
- `add_report(employee)` appends an `Employee` to `reports`.
  - If `employee` is not an `Employee` (use `isinstance`), raise `TypeError("reports must be employees")`.
  - If `employee` is the manager itself, raise `ValueError("a manager cannot report to themselves")`.
- `describe()` returns the parent's text plus `", <n> reports"`: `"Asha (34), id M1, 2 reports"`.

Every check must work from every level: `Manager("X", -1, "M9", 100)` raises the age error.

**Example**

```python
m = Manager("Asha", 34, "M1", 90000)
r = Employee("Ravi", 28, "E7", 50000)
m.add_report(r)
m.add_report(Employee("Neha", 25, "E8", 45000))
print(r.describe())     # Ravi (28), id E7
print(m.describe())     # Asha (34), id M1, 2 reports
print(m.name, m.salary) # Asha 90000
m.add_report("Ravi")    # TypeError: reports must be employees
```
