# Parse and summarise typed rows

Data from outside (a file, the user) is not checked by hints, so a function at the boundary must
validate it. Write four annotated functions in `solution.py`.

A **row** is a line like `"asha, 21"`: a name and an age, separated by a comma.

1. `parse_rows(lines)`: go through the lines and return **two things as a pair**: the list of
   valid rows as `(name, age)` tuples, and the list of bad lines (kept exactly as given).
   - A line that is empty or only spaces is **ignored** (neither valid nor bad).
   - A line is bad if it does not have exactly two comma-separated parts, the name is empty after
     stripping, the age is not a whole number, or the age is outside `0` to `150`.
2. `oldest(rows)`: the row with the highest age (the first one on a tie), or `None` for no rows.
3. `age_buckets(rows)`: a dict with **always these four keys**, each mapping to the list of names
   in that group, in order of appearance: `"child"` (age under 13), `"teen"` (13 to 19), `"adult"`
   (20 to 64) and `"senior"` (65 and over).
4. `mean_age(rows)`: the average age as a decimal, or `None` for no rows.

Choose the hints yourself. They are checked.

**Example**

```python
lines = ["asha, 21", "ravi,17", "", "bad", "zed, abc", "mia, 70", "x, 200", ",5"]
rows, bad = parse_rows(lines)
rows   # [("asha", 21), ("ravi", 17), ("mia", 70)]
bad    # ["bad", "zed, abc", "x, 200", ",5"]
oldest(rows)       # ("mia", 70)
age_buckets(rows)  # {"child": [], "teen": ["ravi"], "adult": ["asha"], "senior": ["mia"]}
mean_age(rows)     # 36.0
```
