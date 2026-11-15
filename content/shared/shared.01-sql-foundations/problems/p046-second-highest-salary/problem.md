# Second highest salary, overall and per department

"The second highest" is harder than it sounds: what if two people share the top salary? Here the rule is **by distinct salary
value**: the second highest is the second value in the list of different salaries, from the top. Do not use window functions
(`OVER`); use the tools of this chapter.

```sql
CREATE TABLE employees (emp_id INTEGER PRIMARY KEY, name TEXT NOT NULL, dept TEXT NOT NULL, salary INTEGER NOT NULL);
INSERT INTO employees VALUES (1,'Ann','Eng',100),(2,'Bob','Eng',90),(3,'Cy','Eng',90),(4,'Dee','Eng',80),(5,'Eli','Ops',70),(6,'Fay','Ops',60),(7,'Gus','Hr',50);
```

- `QUERY_A`: one row, one column `second_highest`: the second-highest **distinct** salary in the whole table. If there is no
  such value (all salaries equal, or fewer than two rows) the single row must contain `NULL`.
- `QUERY_B`: for each department, every employee who earns that department's second-highest distinct salary. Columns `dept`, `name`,
  `salary`, ordered by `dept`, then `name`. Departments with only one distinct salary have no second-highest and do not appear.

**Example.** Salaries: 100, 90, 90, 80, 70, 60, 50. Distinct, descending: 100, 90, 80, ... so `QUERY_A` is `90`.
In `Eng`, salaries 100, 90, 90, 80: the second distinct is 90, and **both** Bob and Cy earn it, so both rows appear.
In `Ops`: 70, 60: Fay. In `Hr`: only one salary, so nothing.
