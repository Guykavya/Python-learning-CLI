# A disassembler for the mini VM

`dis.dis(f)` turns CPython's bytecode back into a readable listing: one line per instruction
with its offset, its name and its operand, and a label (`L1:`, `L2:`) wherever some jump lands.
Write the same tool for the bytecode of the module project (p035).

A program is a list of `(op, arg)` tuples using the mini instruction set:

| Op | `arg` |
|---|---|
| `PUSH` | an int |
| `LOAD`, `STORE` | a variable name (str) |
| `JUMP`, `JUMP_IF_FALSE` | a target offset (int) |
| `CALL` | a tuple `(target offset, nargs)` |
| `POP` `DUP` `SWAP` `ADD` `SUB` `MUL` `DIV` `LT` `EQ` `PRINT` `RET` `HALT` | `None` |

Copy `starter.py` to `solution.py` and write three functions.

**`jump_targets(program)`** returns the sorted list of distinct offsets that some `JUMP`,
`JUMP_IF_FALSE` or `CALL` goes to. A target may be anything from `0` to `len(program)` (the
end of the program). Raise `ValueError` for an unknown op or a target outside that range.

**`disassemble(program)`** returns the listing as a list of strings:

- Labels are named `L1`, `L2`, ... in increasing **offset** order (the smallest target is `L1`),
  not in the order the jumps appear.
- Before the instruction at a target offset comes a line `L1:`. A target equal to
  `len(program)` gets its label line after the last instruction.
- Each instruction line is `f"{offset:>4}  {op:<13} {operand}"` with trailing spaces removed.
  The operand text is the number or name for `PUSH`/`LOAD`/`STORE`, the label for the jumps,
  `"<label> <nargs>"` for `CALL`, and nothing for the other ops.
- It raises `ValueError` in the same cases as `jump_targets`.

**`to_assembly(program)`** returns assembler text that the p035 assembler would turn back
into the same program: label lines `L1:` at the left margin, each instruction as
`"    OP operand"` (four spaces), every line ending in `"\n"`.

**Example**

```python
program = [
    ("PUSH", 3), ("STORE", "n"),
    ("LOAD", "n"), ("JUMP_IF_FALSE", 12),          # 2, 3
    ("LOAD", "n"), ("CALL", (13, 1)), ("PRINT", None),
    ("LOAD", "n"), ("PUSH", 1), ("SUB", None), ("STORE", "n"),
    ("JUMP", 2),                                    # 11
    ("HALT", None),                                 # 12
    ("DUP", None), ("MUL", None), ("RET", None),    # 13: square(x)
]
jump_targets(program)    # [2, 12, 13]
print("\n".join(disassemble(program)))
```

```
   0  PUSH          3
   1  STORE         n
L1:
   2  LOAD          n
   3  JUMP_IF_FALSE L2
   4  LOAD          n
   5  CALL          L3 1
   6  PRINT
   7  LOAD          n
   8  PUSH          1
   9  SUB
  10  STORE         n
  11  JUMP          L1
L2:
  12  HALT
L3:
  13  DUP
  14  MUL
  15  RET
```

`to_assembly([("PUSH", 0), ("JUMP_IF_FALSE", 3), ("CALL", (3, 0)), ("RET", None)])` returns
`"    PUSH 0\n    JUMP_IF_FALSE L1\n    CALL L1 0\nL1:\n    RET\n"`.
