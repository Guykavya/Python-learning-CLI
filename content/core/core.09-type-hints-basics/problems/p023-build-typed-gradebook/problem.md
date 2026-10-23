# Build a typed gradebook module

Write a complete, annotated `solution.py` from this specification. `starter.py` has the five
function names with empty bodies. You decide every hint, and the module must also behave
correctly. Aim for code that would pass `python -m mypy --strict`.

A **line** looks like `"asha, 70"`: a name, a comma, a score.

1. `parse_line(line)`: return `(name, score)` with the name stripped of spaces and the score as an
   `int`. Return `None` if the line is bad: it does not split into **exactly two** parts at the
   commas, the name is empty after stripping, the score is not a whole number, or the score is
   outside `0` to `100`.
2. `load(lines)`: build a dict from each name to the list of their scores, in order. Bad lines are
   skipped.
3. `average(scores)`: the mean of a list of scores as a decimal; `0.0` for an empty list.
4. `best_student(book)`: the name with the highest average; if two are tied, the one that comes
   first alphabetically; `None` for an empty book.
5. `ranking(book)`: a list of `(name, average)` pairs, highest average first; ties broken by name,
   alphabetically.
6. `report(book)`: a list of text lines, one per student in ranking order, in the form
   `"asha: 80.0"` (the average with exactly one decimal).

**Example**

```python
lines = ["asha, 70", "ravi, 60", "bad line", "asha, 90", "zed, 101", "mia, 80"]
book = load(lines)         # {"asha": [70, 90], "ravi": [60], "mia": [80]}
best_student(book)         # "asha"   (asha and mia both average 80.0)
ranking(book)              # [("asha", 80.0), ("mia", 80.0), ("ravi", 60.0)]
report(book)               # ["asha: 80.0", "mia: 80.0", "ravi: 60.0"]
```
