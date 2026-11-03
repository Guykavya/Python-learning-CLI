## Approach

`QUERY_A`: `DISTINCT` first removes repeated salaries, `ORDER BY ... DESC` lists them from the top, `LIMIT 1 OFFSET 1` skips the first and takes the next. Wrapping it in `SELECT (...)` turns "no row" into a single `NULL`.

`QUERY_B`: an employee has the second-highest distinct salary in their department when exactly **one** different salary in that department is higher. The correlated `COUNT(DISTINCT ...)` counts those higher salaries. Ties share the same count, so all of them are returned.

## Code

```sql
-- QUERY_A
SELECT (SELECT DISTINCT salary
        FROM employees
        ORDER BY salary DESC
        LIMIT 1 OFFSET 1) AS second_highest;

-- QUERY_B
SELECT e.dept, e.name, e.salary
FROM employees e
WHERE (SELECT COUNT(DISTINCT e2.salary)
       FROM employees e2
       WHERE e2.dept = e.dept AND e2.salary > e.salary) = 1
ORDER BY e.dept, e.name;
```

## Complexity

`QUERY_A`: sort the distinct salaries, O(n log n) (an index on `salary` makes it nearly free). `QUERY_B`: one correlated subquery per employee, O(n x department size) without an index, usually fine for small groups.

## Another way / portable SQL

`QUERY_A` as `SELECT MAX(salary) FROM employees WHERE salary < (SELECT MAX(salary) FROM employees)`: returns NULL when no second value exists, no `OFFSET` needed. The general "Nth" version is `COUNT(DISTINCT higher salaries) = N - 1`. Window functions (`DENSE_RANK() OVER (PARTITION BY dept ORDER BY salary DESC) = 2`) express `QUERY_B` in one line and are covered later; MySQL < 8 had no windows, which is why the correlated forms are still common in interviews.
