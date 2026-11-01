## Approach

The model answer is in `answer.md`. The key idea: bytecode is a list of tiny steps on a value
stack, and local variables sit in numbered slots of the frame, so reading a listing is just
replaying pushes and pops.

| Instruction (3.14) | Pops | Pushes |
|---|---|---|
| `LOAD_FAST_BORROW_LOAD_FAST_BORROW` | 0 | 2 |
| `BINARY_OP` | 2 | 1 |
| `STORE_FAST` | 1 | 0 |
| `LOAD_FAST_BORROW`, `LOAD_SMALL_INT` | 0 | 1 |
| `RETURN_VALUE` | 1 | 0 (leaves the frame) |

## Check your answer

- Did you say the line number appears only on the first instruction of each source line?
- Does your stack table end with `[13]` before `RETURN_VALUE`, and is it empty after `STORE_FAST`?
- Did you say that `result` is stored in a local slot of the frame, found by index?
- Did you connect the special instructions with "fewer, cheaper trips round the evaluation loop"?
- Did you say that tools should use code object attributes or behaviour, not exact listings?

## Another way

Check every claim yourself: `dis.stack_effect(dis.opmap["BINARY_OP"], 0)` returns `-1` (two
pops, one push), and `[(i.opname, i.argval) for i in dis.get_instructions(area)]` gives the
listing as data. Run the same function on another Python version, if you have one, and compare.
