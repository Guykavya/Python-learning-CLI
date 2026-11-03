## Hint 1

For `QUERY_A`: if you list the distinct salaries from the top, which row do you want, and how do you skip the first? And what does a
subquery that returns no row give you when used as a value?

For `QUERY_B`: how can you say "exactly one distinct salary in my department is higher than mine"? What would you count, and
with which condition on `dept`?

## Hint 2

```
QUERY_A:
SELECT ( SELECT DISTINCT salary FROM employees
         ORDER BY salary DESC LIMIT 1 OFFSET ? ) AS second_highest;

QUERY_B:
SELECT e.dept, e.name, e.salary
FROM employees e
WHERE ( SELECT COUNT(DISTINCT e2.salary)
        FROM employees e2
        WHERE e2.dept = e.? AND e2.salary > e.? ) = ?
ORDER BY e.dept, e.name;
```
