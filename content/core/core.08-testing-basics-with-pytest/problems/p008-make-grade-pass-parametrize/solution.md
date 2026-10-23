## Approach

Reject impossible marks first, so the other branches can assume `0 <= marks <= 100`. Then walk down from the highest grade with `>=`. Because each `if` returns, reaching a branch already means all the higher thresholds were missed, so each test needs only its lower limit.

## Code

```python
def grade(marks):
    if marks < 0 or marks > 100:
        raise ValueError(f"marks must be from 0 to 100, got {marks}")
    if marks >= 90:
        return "A"
    if marks >= 75:
        return "B"
    if marks >= 60:
        return "C"
    if marks >= 40:
        return "D"
    return "F"
```

## Complexity

O(1).

## Another way

A list of `(limit, letter)` pairs, `[(90, "A"), (75, "B"), ...]`, and a loop returning the first letter whose limit is at most `marks`.
