## Hint 1

Which clause inside `OVER (...)` decides the order in which rows are numbered? Does the `ORDER BY` of the whole
query also number the rows, or only sort them at the end?

## Hint 2

Two sort keys are needed inside the window: salary high to low, then name.

```
SELECT name, salary,
       ROW_NUMBER() OVER (ORDER BY <salary desc>, <name>) AS rn
FROM employees
ORDER BY rn
```
