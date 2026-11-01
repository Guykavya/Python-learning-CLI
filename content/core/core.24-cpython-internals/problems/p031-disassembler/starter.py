"""A disassembler for the mini VM's bytecode (the instruction set of the module project, p035)."""

NO_ARG = {"POP", "DUP", "SWAP", "ADD", "SUB", "MUL", "DIV", "LT", "EQ", "PRINT", "RET", "HALT"}
JUMPS = {"JUMP", "JUMP_IF_FALSE"}
KNOWN = NO_ARG | JUMPS | {"PUSH", "LOAD", "STORE", "CALL"}


def jump_targets(program):
    """Sorted list of the distinct offsets that some JUMP, JUMP_IF_FALSE or CALL goes to."""
    return []


def disassemble(program):
    """A listing: one line per instruction (offset, op, operand), label lines before targets."""
    return [f"{offset} {op} {arg}" for offset, (op, arg) in enumerate(program)]


def to_assembly(program):
    """Assembler text that the p035 assembler turns back into the same program."""
    return ""
