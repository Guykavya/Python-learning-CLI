## Approach

`group_scores` creates the empty dict with its hint (`dict[str, list[int]]`, otherwise mypy reports `Need type annotation`), then for every pair appends the score to that student's list, creating the list the first time with `setdefault`.

`best_per_student` is a dict comprehension: same keys, `max` of each list. `students_above` computes each average with `/` and keeps the names above the limit, then `sorted(...)` returns a `list[str]`. The `limit` is hinted as `float`, so callers may pass an `int` too.

## Code

```python
def group_scores(pairs: list[tuple[str, int]]) -> dict[str, list[int]]:
    groups: dict[str, list[int]] = {}
    for name, score in pairs:
        groups.setdefault(name, []).append(score)
    return groups


def best_per_student(groups: dict[str, list[int]]) -> dict[str, int]:
    return {name: max(scores) for name, scores in groups.items()}


def students_above(groups: dict[str, list[int]], limit: float) -> list[str]:
    return sorted(name for name, scores in groups.items() if sum(scores) / len(scores) > limit)
```

## Complexity

O(n) for the grouping and the best scores, O(n + k log k) for `students_above` with k students.

## Another way

`collections.defaultdict(list)` removes the `setdefault` call. You would still need a hint, `groups: defaultdict[str, list[int]]`, and that is a topic for a later module.
