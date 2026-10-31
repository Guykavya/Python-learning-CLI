## Approach

Walk through the commands one by one, keeping the frame's variables in a table. A stop at a
line means that line is **about to** run.

| Command | Where pdb stops | name | cost | total | Snapshot |
|---|---|---|---|---|---|
| (start) | line 8 | - | - | - | |
| `b 11, qty > 1` | (sets breakpoint 1) | | | | |
| `c` | line 11, pen (qty 3 > 1) | pen | 30 | 0 | `A pen 30 0` |
| `n` | line 9 (the `for` again) | pen | 30 | 30 | `B pen 30 30` |
| `n` | line 10 (book unpacked) | book | 30 | 30 | `C book 30 30` |
| `c` | line 11 skipped for book (qty 1), stops for bag (qty 2) | bag | 900 | 150 | `D bag 900 150` |
| `cl 1`, `b 12` | breakpoint 1 deleted, breakpoint 2 on line 12 | | | | |
| `c` | line 11 for ink does not stop any more; stops at line 12 | ink | 5 | 1055 | `E ink 5 1055` |
| `c` | the function returns | | | | |

`total` at D: 30 (pen) + 120 (book) = 150; the bag's 900 is not added yet.
At E: 150 + 900 + 5 = 1055. The loop variables keep their last values after a `for` loop ends,
so `name` is still `ink` at line 12.

Two lessons for real debugging:

- **B and C** are the classic confusion: in a `for` loop, the `for` line is where the next item
  is fetched, so between the end of the body and the `for` line, the variables still hold the
  **previous** item.
- A **conditional breakpoint** (`b 11, qty > 1`) skips the boring iterations without changing
  the code.

## Output

```text
A pen 30 0
B pen 30 30
C book 30 30
D bag 900 150
E ink 5 1055
result 1055
```
