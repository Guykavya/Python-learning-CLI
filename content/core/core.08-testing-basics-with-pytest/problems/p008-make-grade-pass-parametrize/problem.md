# Make the failing tests pass: grade

`test_solution.py` uses `@pytest.mark.parametrize`: one test function, many rows of data. pytest
runs it once per row and reports each row separately (chapter section 9). Read the table of
rows: it is the specification of `grade(marks)`.

Write `grade(marks)` so that every row passes. From the table you can read the rules:

| marks | grade |
|---|---|
| 90 to 100 | `"A"` |
| 75 to 89 | `"B"` |
| 60 to 74 | `"C"` |
| 40 to 59 | `"D"` |
| 0 to 39 | `"F"` |

Marks outside 0 to 100 raise `ValueError`. Look at which rows sit exactly on the borders (39, 40,
59, 60 ...) and why they are there.

**Examples**

```python
grade(95)    # "A"
grade(75)    # "B"
grade(39)    # "F"
grade(101)   # raises ValueError
```
