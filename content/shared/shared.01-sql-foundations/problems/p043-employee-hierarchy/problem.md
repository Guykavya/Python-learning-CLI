# Employee hierarchy with depth

A **recursive CTE** walks a hierarchy. It has two parts joined by `UNION ALL`: an **anchor** (the starting rows) and a
**recursive step** that uses the CTE itself to find the next level. The database repeats the step until it adds no new rows.

```sql
CREATE TABLE employees (emp_id INTEGER PRIMARY KEY, name TEXT NOT NULL, manager_id INTEGER REFERENCES employees(emp_id));
INSERT INTO employees VALUES (1,'Ria',NULL),(2,'Sam',1),(3,'Tia',1),(4,'Uma',2),(5,'Vik',2),(6,'Wen',4),(7,'Xan',3);
```

Each employee points to their manager (`manager_id`, NULL for people at the top). Return **every** employee with their depth:
top-level people (no manager) have depth 0, their direct reports depth 1, and so on.

| column | meaning |
|---|---|
| `emp_id` | the employee |
| `name` | their name |
| `depth` | number of steps from a top-level person |

Order: `depth` ascending, then `emp_id` ascending. There may be more than one top-level person. Use `WITH RECURSIVE`.

**Example.** Ria (1) is the top: depth 0. Sam (2) and Tia (3) report to Ria: depth 1. Uma, Vik and Xan: depth 2. Wen (6) reports
to Uma (4): depth 3.
