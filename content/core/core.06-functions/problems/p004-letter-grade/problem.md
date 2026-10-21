# Letter grade with early returns

Write `letter_grade(score)` that turns a score into a letter:

| score | grade |
|---|---|
| 90 to 100 | `"A"` |
| 75 to 89 | `"B"` |
| 60 to 74 | `"C"` |
| 40 to 59 | `"D"` |
| 0 to 39 | `"F"` |
| below 0 or above 100 | `"invalid"` |

Scores may be floats such as `89.5` (that is a `"B"`: only 90 and above is an `"A"`).

Use **early returns** (guard clauses): check the invalid case first and `return`, then the
grades from highest to lowest, each with its own `return`. You should not need `elif` or `else`.

**Examples**

```python
letter_grade(95)     # "A"
letter_grade(75)     # "B"
letter_grade(39.9)   # "F"
letter_grade(101)    # "invalid"
```
