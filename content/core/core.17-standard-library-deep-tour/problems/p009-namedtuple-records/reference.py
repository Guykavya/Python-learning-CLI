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
