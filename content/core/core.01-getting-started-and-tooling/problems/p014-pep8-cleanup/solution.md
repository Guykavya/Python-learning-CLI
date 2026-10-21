## Approach

Fix names first (and every use of them), then layout: one statement per line,
spaces around `=` and `+`, a space after commas, nothing between a function
name and `(`.

## Code

```python
student_name = "Asha"
student_age = 19
subject_count = 3
total_marks = 78 + 85 + 91
print("Name:", student_name)
print("Age:", student_age)
print("Subjects:", subject_count)
print("Total:", total_marks)
```

## Why these rules

`snake_case` is the convention every Python programmer expects for variables,
so `StudentName` makes readers think "this is a class". `l` is banned because it
looks like `1` in many fonts. Consistent spacing makes the structure of each
line visible at a glance.

## Another way

Let a tool do the layout: `ruff format solution.py` (or `black`) fixes spacing
and semicolons automatically. No tool can choose good names for you, though.
