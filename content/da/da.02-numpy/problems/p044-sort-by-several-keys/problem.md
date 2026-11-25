# Sort by several keys

Chapter section 15.2 (`lexsort`). A results table is stored as three 1-D arrays of the same length: `names` (strings), `scores` (numbers) and `ages` (integers). Write `sort_records(names, scores, ages)` that returns the **order** (an integer array of row positions) for this ranking:

1. higher `score` first;
2. on equal scores, **younger** first (smaller `age`);
3. on equal score and age, `name` in alphabetical order (`"Asha"` before `"Bilal"`; plain string comparison).
4. Rows equal on all three keys keep their original order.

Use `np.lexsort` (remember: the **last** key is the primary one), no Python `sorted`. Inputs may be lists or arrays; scores may be floats. Empty inputs give an empty integer array. Do not change the inputs.

## Example

```python
names = ["Eli", "Fay", "Gus", "Hal", "Ivy"]
scores = [80, 95, 80, 80, 95]
ages = [15, 14, 13, 15, 14]
order = sort_records(names, scores, ages)
order.tolist()
# [1, 4, 2, 0, 3]
[names[i] for i in order]
# ['Fay', 'Ivy', 'Gus', 'Eli', 'Hal']
```

Fay and Ivy both have 95 and age 14, so the name decides; Gus (80, 13) is younger than Eli and Hal (80, 15), who are then ordered by name.
