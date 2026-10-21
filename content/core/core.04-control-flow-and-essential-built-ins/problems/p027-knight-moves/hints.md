## Hint 1

Instead of working out the 8 possible jumps and then sorting them, try looking at **every**
square of the board in the required order and asking "can the knight reach this one?".

## Hint 2

Turn files into numbers: `"abcdefgh".index(letter)`. A square is a knight move away when the
file distance times the rank distance is exactly 2. Why does that work?

## Hint 3

```
for f in range(8):
    for r in range(1, 9):
        if abs(f - start_f) * abs(r - start_r) == 2: add the square
```
Validate first: the text has 2 characters, the first in `"abcdefgh"`, the second in `"12345678"`.
