## Hint 1

What are the rows you know without any recursion (who has no manager)? Given a row already in the result, how do you find the
rows one level deeper (whose `manager_id` equals that row's `emp_id`)? What should the new depth be?

## Hint 2

```
WITH RECURSIVE tree(emp_id, name, depth) AS (
    SELECT emp_id, name, 0 FROM employees WHERE manager_id IS ?          -- anchor
    UNION ALL
    SELECT e.emp_id, e.name, t.depth + ?                                 -- recursive step
    FROM employees e JOIN tree t ON e.manager_id = t.?
)
SELECT emp_id, name, depth FROM tree ORDER BY depth, emp_id;
```
