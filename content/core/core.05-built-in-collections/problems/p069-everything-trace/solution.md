## Walkthrough

| Code | Output | Why |
|---|---|---|
| `groups` | `{'b': [3], 'a': [1, 2], 'c': [2]}` | letters in first-seen order |
| `len(keys), list(keys)` | `4 ['b', 'a', 'c', 'd']` | the view sees `d`, added after it was made |
| `totals` | `{'b': 3, 'a': 3, 'c': 2}` | `d`'s list is empty, so the filter drops it |
| `ranked` | `[(-3, 'a'), (-3, 'b'), (-2, 'c')]` | tuples sort by the negative total, then the letter |
| `matrix, snapshot` | `[[0, 0, 9], [5, 0]] [[0, 0, 9], [0, 0]]` | `alias` is row 0, so the 9 appears; the snapshot was taken before `matrix[1][0] = 5` |
| set algebra | `[1, 2] [0, 3, 5]` | `{0,1,2,3}` and `{1,2,5}`: common items, then items in exactly one |
| `flat` | `[9, 5]` | non-zero values, row by row |
| `first, rest` | `9 [5]` | sorted high to low, then unpacked |
