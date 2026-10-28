# Merge uneven columns into CSV lines

A teacher keeps a class register as **columns**: one list of names, one list of marks, one list
of grades. Some columns are shorter, because some data is still missing.
You must turn the columns into CSV lines (comma-separated values), one line per row.

Write a **generator function** `csv_lines(columns, fill="")` in `solution.py`.

- `columns` is a list of iterables (lists or generators).
- Row `i` holds item `i` of every column. A column that is too short is filled with `fill`.
- Each row is yielded as one string: the values turned into `str` and joined with `","`.
- The number of rows is the length of the **longest** column.

**Example**

```python
names = ["Ann", "Bob", "Cy"]
marks = [90, 85]
grades = ["A"]
list(csv_lines([names, marks, grades], fill="-"))
# ['Ann,90,A', 'Bob,85,-', 'Cy,-,-']

list(csv_lines([names, marks]))
# ['Ann,90', 'Bob,85', 'Cy,']
```
