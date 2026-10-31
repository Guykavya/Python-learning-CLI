- Forgetting the groups in line 2 and writing the same as line 1.
- Writing `', '` on line 2: only what is inside the parentheses is kept, here just the comma.
- Writing `['x', 'y', 'z']` on line 4: two separators in a row leave an empty piece between them.
- Leaving out the `None`s on line 6, or writing `''` instead of `None`. A group that did not take
  part in the match is `None`, and every match adds one value **per group**.
- Expecting `re.split(r"\s+", ...)` to drop the empty first and last pieces like `str.split()`
  does.
- Counting `maxsplit` as the number of pieces. It is the number of **cuts**: `maxsplit=2` gives
  three pieces.
