## Hint 1

Keep one position for each line, `i` and `j`, both starting at 0. While both lines still have
numbers left, compare `a[i]` and `b[j]`.

## Hint 2

Take the smaller one, add it to the result, and move only **that** line's position forward.
When one line runs out, the rest of the other line is already sorted: add it all.

## Hint 3

Check sortedness with `all(int(x) <= int(y) for x, y in zip(a, a[1:]))`. Convert to `int` for
every comparison: as text, `"10" < "9"`.
