# RANK versus DENSE_RANK with ties

`ROW_NUMBER` never repeats a number. `RANK` and `DENSE_RANK` give equal rows the *same* rank, and they differ in what
comes after a tie:

| salary | RANK | DENSE_RANK |
|---|---|---|
| 90 | 1 | 1 |
| 80 | 2 | 2 |
| 80 | 2 | 2 |
| 70 | 4 | 3 |

`RANK` skips numbers after a tie (like Olympic medals: two silvers, no bronze). `DENSE_RANK` never skips.

Same table as before:

```sql
CREATE TABLE employees (emp_id INTEGER PRIMARY KEY, name TEXT, dept TEXT, salary INTEGER);
INSERT INTO employees VALUES
 (1,'Asha','Eng',90),(2,'Ben','Eng',80),(3,'Chen','Ops',80),(4,'Dina','Ops',70),(5,'Eli','Eng',60);
```

Write one `SELECT` in `QUERY` returning `name`, `salary`, `rnk`, `drnk`: the `RANK` and the `DENSE_RANK` by salary
from high to low. Order the result by `salary` descending, then `name`.

**Example**

| name | salary | rnk | drnk |
|---|---|---|---|
| Asha | 90 | 1 | 1 |
| Ben | 80 | 2 | 2 |
| Chen | 80 | 2 | 2 |
| Dina | 70 | 4 | 3 |
| Eli | 60 | 5 | 4 |
