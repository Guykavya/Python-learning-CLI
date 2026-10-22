## Hint 1

Build `group_scores` with an empty dict. mypy needs to know what the empty dict will hold, so where do you write the hint for it? `dict.setdefault(key, [])` returns the list for the key, creating an empty one if needed.

## Hint 2

For `best_per_student` a dict comprehension over `groups.items()` with `max(...)` works. For `students_above`, compute each average as `sum(scores) / len(scores)`, keep the names whose average is above `limit`, then sort.

## Hint 3

```
def group_scores(pairs):
    groups: dict[str, list[int]] = {}
    for name, score in pairs:
        groups.setdefault(name, []).append(score)
    return groups

def best_per_student(groups):
    return {name: max(s) for name, s in groups.items()}

def students_above(groups, limit):
    return sorted(name for name, s in groups.items() if sum(s) / len(s) > limit)
```
