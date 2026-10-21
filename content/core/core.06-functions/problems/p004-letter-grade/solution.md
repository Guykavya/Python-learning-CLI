## Approach

Guard clauses: reject the invalid range first and return. After that the score is known to be
in range. Test the grades from the top: if a score reaches the `>= 75` line, the `>= 90` test
already failed, so it is below 90. Each `return` ends the call, so no `elif` is needed, and the
final `return "F"` is reached only when everything else failed.

## Code

```python
def letter_grade(score):
    """Return the letter grade for a score from 0 to 100, or "invalid"."""
    if score < 0 or score > 100:
        return "invalid"
    if score >= 90:
        return "A"
    if score >= 75:
        return "B"
    if score >= 60:
        return "C"
    if score >= 40:
        return "D"
    return "F"
```

## Complexity

O(1).

## Another way

A table of `(lower_bound, letter)` pairs and a loop that returns the first letter whose bound the
score reaches. That scales better if there are many grades, and keeps the data separate from the
logic:
```python
BOUNDS = [(90, "A"), (75, "B"), (60, "C"), (40, "D"), (0, "F")]
for bound, letter in BOUNDS:
    if score >= bound:
        return letter
```
