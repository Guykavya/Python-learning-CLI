## Approach

Sort the names, compute each average in a one-line `try`, and choose the line in `except` or
`else`. The `try` contains nothing else, so a mistake while formatting could never be mistaken
for "no marks". `sum` raising `TypeError` is not caught, so bad data is reported loudly.

## Code

```python
def average_report(marks_by_student):
    """Return 'name: average' lines sorted by name; 'no marks yet' for an empty list."""
    lines = []
    for name in sorted(marks_by_student):
        marks = marks_by_student[name]
        try:
            average = sum(marks) / len(marks)
        except ZeroDivisionError:
            lines.append(f"{name}: no marks yet")
        else:
            lines.append(f"{name}: {average:.1f}")
    return lines
```

## Complexity

O(s log s + m) for s students and m marks in total.

## Another way

LBYL: `if not marks: ... else: ...`. For an empty list this check is simple and exact, so many
programmers would prefer it here. The problem uses the `try` form to practise narrow blocks and
`else`.
