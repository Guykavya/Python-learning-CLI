## Approach

Trace the VM like CPython's evaluation loop: fetch the instruction at `pc`, advance `pc`, run
the instruction, print the state. Keep one stack per frame.

## Trace

**Start.** `0 PUSH`: `[2]`. The value on the main stack is the loop counter `n`.

**Round 1 (n = 2).**

- `1 DUP` → `[2, 2]`; `2 JUMP_IF_FALSE` pops `2`, which is not 0, so no jump → `[2]`.
- `3 DUP` → `[2, 2]`; `4 PUSH` → `[2, 2, 10]`.
- `5 CALL (11, 2)`: the top two values `[2, 10]` move into a new frame, the return address is 6,
  `pc = 11`. The caller keeps `[2]`. The line shows the **new** frame: `depth=2 stack=[2, 10]`.
- `11 SWAP` → `[10, 2]`; `12 SUB` → `10 - 2` → `[8]`.
- `13 RET` pops 8, removes the frame (depth 1), pushes 8 on the caller's stack → `[2, 8]`, `pc = 6`.
- `6 PRINT` pops 8 and prints `out 8`, then its trace line shows `[2]`.
- `7 PUSH` → `[2, 1]`; `8 SUB` → `[1]`; `9 JUMP` → `pc = 1`, stack unchanged `[1]`.

**Round 2 (n = 1).** The same steps give `10 - 1 = 9`: `out 9`, and the round ends with `[0]`.

**End (n = 0).** `1 DUP` → `[0, 0]`; `2 JUMP_IF_FALSE` pops 0 and jumps to 10 → `[0]`;
`10 HALT` sets `pc = len(program)` and its line still prints, `[0]`. The loop ends.

```
0 PUSH depth=1 stack=[2]
1 DUP depth=1 stack=[2, 2]
2 JUMP_IF_FALSE depth=1 stack=[2]
3 DUP depth=1 stack=[2, 2]
4 PUSH depth=1 stack=[2, 2, 10]
5 CALL depth=2 stack=[2, 10]
11 SWAP depth=2 stack=[10, 2]
12 SUB depth=2 stack=[8]
13 RET depth=1 stack=[2, 8]
out 8
6 PRINT depth=1 stack=[2]
...
```

28 instruction lines (1 + 2 rounds of 12 + 3) plus 2 `out` lines = 30 lines.

## Another way

Run the program in the real project VM (p035) with `vm.step()` in a loop and print `vm.pc` and
`vm.stack` after each step; or write the program as assembler text and let your disassembler
(p031) show the labels. Comparing with your hand trace is how CPython developers debug the real
evaluation loop: with `dis` and a step-by-step tracer.
