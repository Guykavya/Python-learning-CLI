## Hint 1

Keep a small table with the columns `line`, `name`, `cost`, `total`, and update it as pdb
moves. Remember a stop at line N means line N has **not** run yet. Which item is the first one
with `qty > 1`?

## Hint 2

After `A`, `n` runs line 11 (`total` changes) and stops at line 9, **before** the `for` takes
the next item: `name` and `cost` still belong to the pen. The next `n` runs line 9 (the next
item is unpacked) and stops at line 10, before `cost` is recomputed.

```
A: stop at 11, pen    cost 30   total 0
B: stop at 9          total 30, name still pen
C: stop at 10         name book, cost still 30
D: next stop at 11 with qty > 1 -> which item? total before adding it?
E: breakpoint 1 is gone; stop at 12 after the loop ends
```
