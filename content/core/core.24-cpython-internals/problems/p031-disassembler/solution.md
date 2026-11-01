## Approach

A disassembler needs **two passes**, like the assembler it undoes. The first pass collects every
jump target (`arg` for the jumps, `arg[0]` for `CALL`) and checks it. Sorting the distinct targets
and numbering them gives the label names. The second pass prints the program: a label line
whenever the current offset is a target, then the instruction itself with a fixed-width format.
The target `len(program)` has no instruction, so its label is printed after the loop.

`to_assembly` is the same walk with a different line format; sharing `label_names` and
`_arg_text` guarantees that the listing and the assembly text always agree.

## Code

```python
NO_ARG = {"POP", "DUP", "SWAP", "ADD", "SUB", "MUL", "DIV", "LT", "EQ", "PRINT", "RET", "HALT"}
JUMPS = {"JUMP", "JUMP_IF_FALSE"}
KNOWN = NO_ARG | JUMPS | {"PUSH", "LOAD", "STORE", "CALL"}


def _target(op, arg):
    if op in JUMPS:
        return arg
    if op == "CALL":
        return arg[0]
    return None


def jump_targets(program):
    targets = set()
    for offset, (op, arg) in enumerate(program):
        if op not in KNOWN:
            raise ValueError(f"unknown op {op!r} at offset {offset}")
        target = _target(op, arg)
        if target is not None:
            if not 0 <= target <= len(program):
                raise ValueError(f"bad target {target} at offset {offset}")
            targets.add(target)
    return sorted(targets)


def label_names(program):
    return {target: f"L{number}" for number, target in enumerate(jump_targets(program), start=1)}


def _arg_text(op, arg, labels):
    if op in NO_ARG:
        return ""
    if op in JUMPS:
        return labels[arg]
    if op == "CALL":
        target, nargs = arg
        return f"{labels[target]} {nargs}"
    return str(arg)


def disassemble(program):
    labels = label_names(program)
    lines = []
    for offset, (op, arg) in enumerate(program):
        if offset in labels:
            lines.append(f"{labels[offset]}:")
        lines.append(f"{offset:>4}  {op:<13} {_arg_text(op, arg, labels)}".rstrip())
    if len(program) in labels:
        lines.append(f"{labels[len(program)]}:")
    return lines


def to_assembly(program):
    labels = label_names(program)
    lines = []
    for offset, (op, arg) in enumerate(program):
        if offset in labels:
            lines.append(f"{labels[offset]}:")
        lines.append(f"    {op} {_arg_text(op, arg, labels)}".rstrip())
    if len(program) in labels:
        lines.append(f"{labels[len(program)]}:")
    return "\n".join(lines) + "\n"
```

This is what `dis` does too: since Python 3.13 its listings show `L1:`, `L2:` labels for jump
targets instead of raw offsets, computed by a first pass over the instructions (older versions
mark targets with `>>`).

## Complexity

O(n log n) for n instructions: one pass to collect targets, a sort of at most n targets, one
pass to print. Memory O(n) for the lines.

## Another way

Walk the offsets `0 .. len(program)` in **one** loop (note the `+ 1`): at each offset first
yield the label if there is one, then the instruction if `offset < len(program)`. A generator
that yields `("label", text)` and `("ins", offset, op, text)` items can then feed both output
formats, and the special case for the end label disappears.
