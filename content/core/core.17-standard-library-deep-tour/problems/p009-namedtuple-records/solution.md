## Approach

`namedtuple("Employee", ["name", "dept", "salary"], defaults=[0])` builds a new class. Each
instance is a tuple, so it is immutable, unpacks, compares field by field and uses little
memory, but every field also has a name. `defaults` fill the **rightmost** fields, so only `salary`
gets one.

- **parse_rows** cleans each cell with `strip()`, converts the salary when there is one, and
  unpacks the list into the constructor with `*`. Empty rows are skipped first.
- **give_raise** cannot change a tuple, so it builds a new one: `_replace(salary=...)` copies all
  fields and swaps the ones you name. Integer `//` keeps the salary an `int`.
- **dept_totals** is a running sum in a dict; dicts keep first-seen order.
- **to_dicts** uses `_asdict()`, which returns a dict in field order (handy for `json.dumps` or
  `csv.DictWriter`).

The underscore in `_replace` and friends does **not** mean "private" here: it avoids clashes with
field names you might choose (a field could be called `replace`).

## Code

```python
from collections import namedtuple

Employee = namedtuple("Employee", ["name", "dept", "salary"], defaults=[0])


def parse_rows(rows: list[list[str]]) -> list[Employee]:
    result = []
    for row in rows:
        if not row:
            continue
        cells: list = [cell.strip() for cell in row]
        if len(cells) == 3:
            cells[2] = int(cells[2])
        result.append(Employee(*cells))
    return result


def give_raise(emp: Employee, percent: int) -> Employee:
    return emp._replace(salary=emp.salary + emp.salary * percent // 100)


def dept_totals(emps: list[Employee]) -> dict[str, int]:
    totals: dict[str, int] = {}
    for emp in emps:
        totals[emp.dept] = totals.get(emp.dept, 0) + emp.salary
    return totals


def to_dicts(emps: list[Employee]) -> list[dict]:
    return [emp._asdict() for emp in emps]
```

## Complexity

All functions are O(n) for n rows or employees.

## Another way

`typing.NamedTuple` gives the same kind of class with a `class` statement and type hints:

```python
from typing import NamedTuple

class Employee(NamedTuple):
    name: str
    dept: str
    salary: int = 0
```

It is the more readable choice when you want types or methods. Choose a `@dataclass` (core.15)
instead when the record must be mutable or should not compare equal to plain tuples.
