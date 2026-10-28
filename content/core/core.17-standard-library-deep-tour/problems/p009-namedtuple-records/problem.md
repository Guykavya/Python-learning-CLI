# namedtuple: light, readable records

`row[2]` tells a reader nothing. `row.salary` does. `collections.namedtuple` makes a tuple
subclass whose fields have names: it is still a tuple (immutable, unpackable, cheap, comparable),
but readable. It also has helpers: `_make(iterable)`, `_replace(**changes)`, `_asdict()` and
`_fields`.

In `solution.py`:

1. Create `Employee = namedtuple(...)` with the fields `name`, `dept`, `salary`, in that order.
   `salary` has a **default of `0`**.
2. `parse_rows(rows: list[list[str]]) -> list[Employee]`: each row is `[name, dept, salary]` as
   strings (as `csv.reader` gives them). Strip spaces from each cell and convert `salary` to `int`.
   A row with only two cells gets the default salary. Skip rows that are completely empty (`[]`).
3. `give_raise(emp: Employee, percent: int) -> Employee`: a **new** `Employee` with
   `salary + salary * percent // 100`. The original must not change (it cannot: it is a tuple).
4. `dept_totals(emps: list[Employee]) -> dict[str, int]`: total salary per department, in the
   order the departments first appear.
5. `to_dicts(emps: list[Employee]) -> list[dict]`: one plain `dict` per employee, keys in field order.

**Example**

```python
rows = [["Asha", "eng", "50000"], [" Ben ", " ops", " 40000 "], ["Cy", "eng"]]
emps = parse_rows(rows)
emps[1]                   # Employee(name='Ben', dept='ops', salary=40000)
emps[2].salary            # 0
give_raise(emps[0], 10)   # Employee(name='Asha', dept='eng', salary=55000)
dept_totals(emps)         # {'eng': 50000, 'ops': 40000}
to_dicts(emps[:1])        # [{'name': 'Asha', 'dept': 'eng', 'salary': 50000}]
```
