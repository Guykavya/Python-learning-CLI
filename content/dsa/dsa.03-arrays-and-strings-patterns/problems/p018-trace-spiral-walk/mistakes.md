- Using the old boundary in a side: the right side reads rows 1..2, not 0..2, because `top` already moved.
- Reading the bottom row forwards. `range(right, left - 1, -1)` counts down: 11, 10, 9.
- Printing a `bottom` line in the second lap. The `if` is false, so nothing is printed at all (not even `[]`).
- Forgetting the `left []` line: the `if left <= right` check is `1 <= 1`, true, so the line is printed even though the
  range is empty.
- Writing the boundaries before shrinking. The program changes the boundary first and prints after.
