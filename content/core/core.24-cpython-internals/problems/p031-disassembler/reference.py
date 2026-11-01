"""A disassembler for the mini VM's bytecode (the instruction set of the module project, p035)."""

NO_ARG = {"POP", "DUP", "SWAP", "ADD", "SUB", "MUL", "DIV", "LT", "EQ", "PRINT", "RET", "HALT"}
JUMPS = {"JUMP", "JUMP_IF_FALSE"}
KNOWN = NO_ARG | JUMPS | {"PUSH", "LOAD", "STORE", "CALL"}


def _target(op, arg):
    """The jump target of an instruction, or None if it does not jump."""
    if op in JUMPS:
        return arg
    if op == "CALL":
        return arg[0]
    return None


def jump_targets(program):
    """Sorted list of the distinct offsets that some JUMP, JUMP_IF_FALSE or CALL goes to."""
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
    """{target offset: 'L1', ...}, numbered in increasing offset order."""
    return {target: f"L{number}" for number, target in enumerate(jump_targets(program), start=1)}


def _arg_text(op, arg, labels):
    if op in NO_ARG:
        return ""
    if op in JUMPS:
        return labels[arg]
    if op == "CALL":
        target, nargs = arg
        return f"{labels[target]} {nargs}"
    return str(arg)  # PUSH n, LOAD name, STORE name


def disassemble(program):
    """A listing: one line per instruction (offset, op, operand), label lines before targets."""
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
    """Assembler text that the p035 assembler turns back into the same program."""
    labels = label_names(program)
    lines = []
    for offset, (op, arg) in enumerate(program):
        if offset in labels:
            lines.append(f"{labels[offset]}:")
        lines.append(f"    {op} {_arg_text(op, arg, labels)}".rstrip())
    if len(program) in labels:
        lines.append(f"{labels[len(program)]}:")
    return "\n".join(lines) + "\n"
