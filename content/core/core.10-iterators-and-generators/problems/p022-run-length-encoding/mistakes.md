- `len(group)`: a group is an iterator and has no length. Use `sum(1 for _ in group)` or `len(list(group))`.
- Sorting the text first: then `"WWWWBBBW"` gives `[('B', 3), ('W', 5)]`, which is a count of
  letters, not RLE, and cannot be decoded back.
- Saving the `group` objects and reading them later: after `groupby` moves on, old groups are empty.
- In `decode`, adding `str(count)` to the output instead of repeating the character.
