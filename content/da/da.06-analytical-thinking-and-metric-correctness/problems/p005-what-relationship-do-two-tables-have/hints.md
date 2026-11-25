## Hint 1

Which pandas property tells you whether a column has no repeated value? How many combinations of "left unique?" and
"right unique?" are there, and which word does each get? To count orphans: which method asks "is this value in that column?"

## Hint 2

```text
left_unique  = left[left_key].is_unique
right_unique = right[right_key].is_unique
word = lookup of (left_unique, right_unique) in a small dict of four entries
left_orphans  = number of left rows where NOT left[left_key].isin(right[right_key])
right_orphans = the same, the other way round
return a dict with the three entries
```
