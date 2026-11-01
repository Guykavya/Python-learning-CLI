# Simulate a tiny stack machine

CPython runs bytecode on a **value stack**: `LOAD_...` instructions push, `BINARY_OP` pops two
values and pushes one, `STORE_...` pops. The number of values an instruction removes and adds is
its **stack effect**, and the compiler uses those effects to work out `co_stacksize`, the largest
the stack can get, so the frame can reserve exactly that much room.

You will build the same idea for a made-up instruction set (the one used again in later
problems). A program is a list of `(op, arg)` tuples; `arg` is `None` when an op takes none.

| Op | Stack before → after (top on the right) |
|---|---|
| `("PUSH", n)` | `... → ..., n` |
| `("POP", None)` | `..., a → ...` |
| `("DUP", None)` | `..., a → ..., a, a` |
| `("SWAP", None)` | `..., a, b → ..., b, a` |
| `("ADD", None)` | `..., a, b → ..., a + b` |
| `("MUL", None)` | `..., a, b → ..., a * b` |

Copy `starter.py` to `solution.py` (it already defines `StackUnderflow`) and write:

**`simulate(ops)`** runs the program on an empty stack and returns the final stack as a list,
bottom first. The **offset** of an instruction is its index in `ops`.

- If an instruction needs more values than the stack holds, raise `StackUnderflow` with a
  message that contains `offset <i>`, for example `"ADD at offset 1 needs 2 values, stack has 1"`.
- An unknown op raises `ValueError` whose message contains the op name.
- Do not change the `ops` list.

**`max_depth(ops)`** returns the largest number of values that were on the stack at any moment
while running the program (`0` for an empty program). It raises the same errors as `simulate`.

**Example**

```python
prog = [("PUSH", 2), ("PUSH", 3), ("ADD", None), ("PUSH", 4), ("MUL", None)]
simulate(prog)                              # [20]      ((2 + 3) * 4)
max_depth(prog)                             # 2
simulate([("PUSH", 1), ("PUSH", 2), ("SWAP", None)])   # [2, 1]
simulate([("PUSH", 1), ("ADD", None)])
# StackUnderflow: ADD at offset 1 needs 2 values, stack has 1
```
