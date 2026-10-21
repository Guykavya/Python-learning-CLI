## Approach

Scan the whole board in the order the output needs. For each square, test the knight rule.
The order comes for free, with no sorting.

## Code

```python
files = "abcdefgh"
square = input().strip().lower()
if len(square) != 2 or square[0] not in files or square[1] not in "12345678":
    print("invalid square")
else:
    start_f = files.index(square[0])
    start_r = int(square[1])
    line = ""
    count = 0
    for f in range(8):
        for r in range(1, 9):
            if abs(f - start_f) * abs(r - start_r) == 2:
                line += f"{files[f]}{r} "
                count += 1
    print(line.strip())
    print(f"Moves: {count}")
```

## Why `distance * distance == 2`

The distances are whole numbers of 0 or more. A product of 2 is only possible as 1 x 2 or
2 x 1, which is exactly the L shape. A distance of 0 makes the product 0, so the knight's own
square and straight lines are excluded.

## Why validate before indexing

`square[1]` on a one-character string raises `IndexError`. Checking `len(square) != 2` first,
with `or`, short-circuits before the index is used.

## Another way

Loop over the eight jumps `(1, 2), (2, 1), (-1, 2), ...`, keep those that stay on the board,
and then sort. That needs a list and sorting, from the next chapter. Scanning 64 squares is
cheap and keeps the order automatic.
