# Number the rows with ROW_NUMBER

A *window function* computes a value for each row by looking at a set of related rows, without
collapsing them into one row the way `GROUP BY` does. `ROW_NUMBER() OVER (ORDER BY ...)` gives every
row a unique number 1, 2, 3, ... in the order you choose.

You have this table (the test uses other rows with the same shape):

```sql
CREATE TABLE employees (emp_id INTEGER PRIMARY KEY, name TEXT, dept TEXT, salary INTEGER);
INSERT INTO employees VALUES
 (1,'Asha','Eng',90),(2,'Ben','Eng',80),(3,'Chen','Ops',80),(4,'Dina','Ops',70),(5,'Eli','Eng',60);
```

Write one `SELECT` in `QUERY` that returns, for every employee, the columns `name`, `salary`, `rn`, where
`rn` is the position when employees are sorted by salary from high to low. Two people with the same
salary must still get different numbers: break ties by `name` (A to Z).

The final result must be ordered by `rn`.

**Example**

| name | salary | rn |
|---|---|---|
| Asha | 90 | 1 |
| Ben | 80 | 2 |
| Chen | 80 | 3 |
| Dina | 70 | 4 |
| Eli | 60 | 5 |

Ben and Chen both earn 80. Ben gets 2 because "Ben" sorts before "Chen".

Write the SQL in `solution.py` (copy `starter.py`). Use column names exactly `name`, `salary`, `rn`.
