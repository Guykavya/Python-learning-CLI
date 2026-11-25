# Grades with `np.select`

Chapter sections 8.4 and 12.2. Write `grades(scores)` that turns an array of scores (floats, any shape, `nan` for
an absent student) into an array of grade strings of the **same shape**:

| Score | Grade |
|---|---|
| 90 or more | `"A"` |
| 75 or more (below 90) | `"B"` |
| 60 or more (below 75) | `"C"` |
| 40 or more (below 60) | `"D"` |
| below 40 | `"F"` |
| `nan` | `"missing"` |

Each boundary belongs to the **higher** grade (exactly 90 is an A). Use `np.select`, no Python loops.

## Example

```python
grades(np.array([92, 89.5, 75, 60, 39.9, np.nan])).tolist()
# ['A', 'B', 'B', 'C', 'F', 'missing']
```
