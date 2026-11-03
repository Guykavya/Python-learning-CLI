# Self join: employee and manager

An employee's manager is another row in the **same** table: `manager_id` holds that person's `emp_id`. To print both names
side by side, join the table to itself. Use two different aliases (`e` for the employee, `m` for the manager) so SQL can tell the copies apart.

```sql
CREATE TABLE employees (
  emp_id     INTEGER PRIMARY KEY,
  name       TEXT NOT NULL,
  manager_id INTEGER REFERENCES employees(emp_id),   -- NULL for the top person
  dept       TEXT NOT NULL,
  salary     INTEGER NOT NULL
);
INSERT INTO employees VALUES
 (1, 'Meera', NULL, 'exec', 150000),
 (2, 'Ravi',  1,    'eng',  110000),
 (3, 'Sana',  1,    'ops',   95000),
 (4, 'Tej',   2,    'eng',   90000),
 (5, 'Uma',   2,    'eng',   92000),
 (6, 'Vik',   3,    'ops',   70000);
```

Return `employee` and `manager` (both names) for **every** employee. The top person has no manager: show NULL for
the manager. Row order does not matter. Put the SQL in `QUERY`.

**Example.** Ravi's manager is Meera; Meera's manager is NULL.
