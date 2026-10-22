# Group scores: dict[str, list[int]]

Write three annotated functions in `solution.py`.

1. `group_scores(pairs: list[tuple[str, int]]) -> dict[str, list[int]]`: `pairs` are
   `(student, score)` records. Return a dict from each student to the list of their scores, in the
   order they appeared.
2. `best_per_student(groups: dict[str, list[int]]) -> dict[str, int]`: each student's highest
   score.
3. `students_above(groups: dict[str, list[int]], limit: float) -> list[str]`: the names of the
   students whose **average** is strictly above `limit`, sorted alphabetically.

The hints are part of the tests. Say what is inside every collection.

**Example**

```python
pairs = [("asha", 70), ("ravi", 60), ("asha", 90)]
group_scores(pairs)                        # {"asha": [70, 90], "ravi": [60]}
best_per_student({"asha": [70, 90], "ravi": [60]})      # {"asha": 90, "ravi": 60}
students_above({"asha": [70, 90], "ravi": [60]}, 70)    # ["asha"]
```
