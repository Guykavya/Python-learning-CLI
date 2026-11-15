## Approach

The anchor selects the top-level people with depth 0. The recursive step joins `employees` to the rows already found: an employee whose `manager_id` is a found `emp_id` is one level deeper. The process stops when a step finds nobody new. Because the data has no cycles, it always ends.

## Code

```sql
WITH RECURSIVE tree(emp_id, name, depth) AS (
    SELECT emp_id, name, 0
    FROM employees
    WHERE manager_id IS NULL
    UNION ALL
    SELECT e.emp_id, e.name, t.depth + 1
    FROM employees e
    JOIN tree t ON e.manager_id = t.emp_id
)
SELECT emp_id, name, depth
FROM tree
ORDER BY depth, emp_id;
```

## Complexity

Each employee is produced once (one parent), so the work is about O(n) join lookups, fast with an index on `manager_id`. If the data had a cycle (A manages B, B manages A) the recursion would never stop, so real systems add a depth limit (`WHERE t.depth < 20`) or track the path.

## Another way / portable SQL

PostgreSQL and MySQL 8 use the same `WITH RECURSIVE` syntax (SQL Server omits the word `RECURSIVE`; Oracle has `CONNECT BY`). A fixed number of self joins only works for a known maximum depth, which is why recursion exists.
