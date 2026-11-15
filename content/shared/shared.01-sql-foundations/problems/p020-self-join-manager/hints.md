## Hint 1

Imagine two copies of the table: one lists employees, the other lists managers. Which column of the employee copy matches which column of the manager copy? Which join type keeps an employee even when no manager is found?

## Hint 2

```
SELECT e.name AS employee, m.name AS manager
FROM employees AS e
<join type> employees AS m ON <e.manager_id = m.emp_id>
```
