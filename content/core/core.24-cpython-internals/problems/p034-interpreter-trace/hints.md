## Hint 1

Before tracing, read the program as a human. What is on the stack each time the loop starts
(offset 1)? What does the function at offset 11 compute from its two arguments, given that the
argument pushed **last** (10) is on top? How many times can the loop run before the value tested
by `JUMP_IF_FALSE` is 0?

Then trace with a table, one row per instruction:

| offset | op | frames | current stack after |
|---|---|---|---|

Remember that the line is printed *after* the instruction, and it shows the stack of whichever
frame is current **at that moment** (after `CALL` that is the new frame; after `RET` the caller's).

## Hint 2

One loop round, starting with `n` on the stack:

```
1  DUP            [n, n]
2  JUMP_IF_FALSE  [n]          (pops; n != 0, so no jump)
3  DUP            [n, n]
4  PUSH 10        [n, n, 10]
5  CALL f, 2      caller keeps [n]; new frame gets [n, 10]; depth 2
11 SWAP           [10, n]
12 SUB            [10 - n]
13 RET            back in depth 1: [n, 10 - n]
   out 10 - n     (printed by PRINT, before PRINT's own line)
6  PRINT          [n]
7  PUSH 1         [n, 1]
8  SUB            [n - 1]
9  JUMP           [n - 1]      pc = 1
```

The round runs for `n = 2` and `n = 1`. When `n = 0`, `JUMP_IF_FALSE` jumps to offset 10.
