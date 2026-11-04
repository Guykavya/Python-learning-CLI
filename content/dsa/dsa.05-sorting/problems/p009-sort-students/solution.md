## Approach

Build the tuple key `(-score, name)`. Tuples compare element by element, so the score decides first and the name only breaks ties.

## Code

```python
n = int(input())
students = []
for _ in range(n):
    name, score = input().split()
    students.append((name, int(score)))
students.sort(key=lambda s: (-s[1], s[0]))
for name, score in students:
    print(name, score)
```

## Complexity

O(n log n) time, O(n) memory.

## Another way

Two stable sorts: first by name (ascending), then by score with `reverse=True`. Python's `reverse=True` keeps equal elements in original order, so the names stay A to Z. This also works for strings that cannot be negated.
