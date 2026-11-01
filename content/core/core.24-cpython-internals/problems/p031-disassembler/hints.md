## Hint 1

A label line has to appear *before* the target instruction, but the jump that names it may come
later in the program (a loop jumps back) or earlier (an `if` jumps forward). So can you write the
listing in a single pass over the program, without knowing all targets first? What should the
first pass collect, and how do you turn "the k-th smallest target" into the name `Lk`?

Which instructions have a target, and where is it stored for `CALL`? Which offset is the only
valid target that has no instruction?

## Hint 2

```
jump_targets(program):
    targets = set()
    for offset, (op, arg) in enumerate(program):
        unknown op -> ValueError
        target = arg for JUMP/JUMP_IF_FALSE, arg[0] for CALL, else None
        if target is not None: check 0 <= target <= len(program) else ValueError; add it
    return sorted(targets)

labels = {target: f"L{k}" for k, target in enumerate(jump_targets(program), start=1)}

disassemble(program):
    for offset, (op, arg) in enumerate(program):
        if offset in labels: add f"{labels[offset]}:"
        add f"{offset:>4}  {op:<13} {operand_text(op, arg)}".rstrip()
    if len(program) in labels: add the final label line
```

Write `operand_text` once and use it in both `disassemble` and `to_assembly`.
