## Hint 1

`setdefault` builds the groups in first-seen order of the letters. `keys` is a live view.

## Hint 2

`alias = matrix[0]` is the first row itself. The comprehension `[row[:] for row in matrix]`
copies each row **at that moment**.

## Hint 3

`{x % 4 for x in range(10)}` is `{0, 1, 2, 3}`. The starred name gets a list.
