## Hint 1

`namedtuple("Employee", ["name", "dept", "salary"], defaults=[0])`: defaults apply to the **rightmost** fields. With the type made, `Employee("Cy", "eng")` gets salary 0. How do you turn a list of 2 or 3 cleaned strings into an `Employee`? (Unpack with `*`, or use `Employee._make`, but convert the salary first.)

## Hint 2

Tuples are immutable, so "change the salary" means "make a new tuple with one field different": `emp._replace(salary=...)`. `emp._asdict()` returns a dict with the fields in order. For totals, a `defaultdict(int)` or `dict.get(dept, 0)` keeps first-seen order.

## Hint 3

```
parse_rows(rows):
    out = []
    for row in rows:
        if not row: continue
        cells = [c.strip() for c in row]
        if len(cells) == 3: cells[2] = int(cells[2])
        out.append(Employee(*cells))
    return out

give_raise(emp, pct):  return emp._replace(salary=emp.salary + emp.salary * pct // 100)
dept_totals(emps):     totals[e.dept] = totals.get(e.dept, 0) + e.salary
to_dicts(emps):        [e._asdict() for e in emps]
```
