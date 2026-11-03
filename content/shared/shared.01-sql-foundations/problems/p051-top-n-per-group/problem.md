# Top 2 earners in each department

"Top N per group" is the classic window-function task. A window function cannot be used in `WHERE`
(the filter runs before windows exist), so you number the rows in a subquery or CTE and filter outside it.

```sql
CREATE TABLE employees (emp_id INTEGER PRIMARY KEY, name TEXT, dept TEXT, salary INTEGER);
INSERT INTO employees VALUES
 (1,'Asha','Eng',90),(2,'Ben','Eng',80),(3,'Chen','Ops',80),(4,'Dina','Ops',70),(5,'Eli','Eng',60),(6,'Fay','Ops',70);
```

Write one query returning `dept`, `name`, `salary` for the **two** highest paid employees in each department.
If salaries tie, the lower `emp_id` wins, so every department returns exactly 2 rows (or fewer if it has fewer than 2 people).
Order by `dept`, then `salary` descending, then `emp_id`.

**Example**

| dept | name | salary |
|---|---|---|
| Eng | Asha | 90 |
| Eng | Ben | 80 |
| Ops | Chen | 80 |
| Ops | Dina | 70 |

Dina (emp_id 4) and Fay (emp_id 6) both earn 70; Dina has the lower id and wins the second place.
