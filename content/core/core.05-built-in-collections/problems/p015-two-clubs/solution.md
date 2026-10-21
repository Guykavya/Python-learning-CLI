## Approach

Each question is one set operation. Sets also remove the accidental repeats for free.
Since sets have no order, sort before printing.

## Code

```python
python = set(input().split())
chess = set(input().split())
for label, group in [("Both", python & chess), ("Only Python", python - chess),
                     ("Only Chess", chess - python), ("Either", python | chess)]:
    print(f"{label}: {' '.join(sorted(group)) if group else '-'}")
```

## Complexity

Building the sets is O(n + m). Intersection is O(min(n, m)); union and difference are O(n + m).
Sorting k names is O(k log k).
