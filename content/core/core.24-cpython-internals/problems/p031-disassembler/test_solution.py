import pytest

from solution import disassemble, jump_targets, to_assembly

SQUARES = [
    ("PUSH", 3),            # 0
    ("STORE", "n"),         # 1
    ("LOAD", "n"),          # 2  loop start
    ("JUMP_IF_FALSE", 12),  # 3
    ("LOAD", "n"),          # 4
    ("CALL", (13, 1)),      # 5
    ("PRINT", None),        # 6
    ("LOAD", "n"),          # 7
    ("PUSH", 1),            # 8
    ("SUB", None),          # 9
    ("STORE", "n"),         # 10
    ("JUMP", 2),            # 11
    ("HALT", None),         # 12
    ("DUP", None),          # 13 square(x)
    ("MUL", None),          # 14
    ("RET", None),          # 15
]

SQUARES_LISTING = [
    "   0  PUSH          3",
    "   1  STORE         n",
    "L1:",
    "   2  LOAD          n",
    "   3  JUMP_IF_FALSE L2",
    "   4  LOAD          n",
    "   5  CALL          L3 1",
    "   6  PRINT",
    "   7  LOAD          n",
    "   8  PUSH          1",
    "   9  SUB",
    "  10  STORE         n",
    "  11  JUMP          L1",
    "L2:",
    "  12  HALT",
    "L3:",
    "  13  DUP",
    "  14  MUL",
    "  15  RET",
]


def mini_assemble(text):
    """A tiny version of the p035 assembler, used to check that to_assembly round-trips."""
    labels, rows = {}, []
    for line in text.splitlines():
        line = line.split("#")[0].strip()
        if not line:
            continue
        if line.endswith(":"):
            labels[line[:-1]] = len(rows)
        else:
            rows.append(line.split())
    program = []
    for op, *args in rows:
        if op == "PUSH":
            program.append((op, int(args[0])))
        elif op in ("LOAD", "STORE"):
            program.append((op, args[0]))
        elif op in ("JUMP", "JUMP_IF_FALSE"):
            program.append((op, labels[args[0]]))
        elif op == "CALL":
            program.append((op, (labels[args[0]], int(args[1]))))
        else:
            assert not args, f"{op} takes no operand, but to_assembly wrote {args}"
            program.append((op, None))
    return program


# ------------------------------------------------------------------ jump_targets
def test_jump_targets_sorted_and_distinct():
    assert jump_targets(SQUARES) == [2, 12, 13], (
        "Collect the targets of JUMP, JUMP_IF_FALSE and CALL (CALL's target is arg[0]), without duplicates, sorted."
    )


def test_jump_targets_none():
    assert jump_targets([("PUSH", 1), ("PRINT", None)]) == [], "A program without jumps has no targets."


def test_jump_targets_duplicates():
    prog = [("PUSH", 0), ("JUMP_IF_FALSE", 3), ("JUMP", 3), ("HALT", None)]
    assert jump_targets(prog) == [3], "Two jumps to the same offset give ONE target."


def test_push_value_is_not_a_target():
    prog = [("PUSH", 1), ("PUSH", 0), ("POP", None), ("POP", None)]
    assert jump_targets(prog) == [], "PUSH's operand is a value, not an offset. Only jumps and CALL have targets."


# ------------------------------------------------------------------ disassemble
def test_full_listing():
    got = disassemble(SQUARES)
    assert got == SQUARES_LISTING, (
        "Check the format: offset right-aligned in 4 columns, two spaces, op left-aligned in 13 columns, "
        "a space, the operand; no trailing spaces; a 'Lk:' line before each target."
    )


def test_instruction_line_format():
    assert disassemble([("PUSH", -5)]) == ["   0  PUSH          -5"], (
        "Use f'{offset:>4}  {op:<13} {operand}'. Negative numbers are printed with str()."
    )
    assert disassemble([("ADD", None)]) == ["   0  ADD"], "Ops without an operand: strip the trailing spaces (.rstrip())."


def test_long_offsets_align():
    prog = [("PUSH", 1)] * 120
    lines = disassemble(prog)
    assert lines[5] == "   5  PUSH          1" and lines[119] == " 119  PUSH          1", (
        "Offsets are right-aligned in a field of width 4."
    )


def test_labels_numbered_by_offset_not_by_first_use():
    prog = [
        ("JUMP", 4),            # 0: the first jump goes to the LATER target
        ("PUSH", 1),            # 1  <- target of the jump at 3
        ("PRINT", None),        # 2
        ("JUMP", 1),            # 3
        ("HALT", None),         # 4
    ]
    assert disassemble(prog) == [
        "   0  JUMP          L2",
        "L1:",
        "   1  PUSH          1",
        "   2  PRINT",
        "   3  JUMP          L1",
        "L2:",
        "   4  HALT",
    ], "Number labels in increasing OFFSET order (L1 is the smallest target), not in the order jumps appear."


def test_label_at_end():
    prog = [("PUSH", 0), ("JUMP_IF_FALSE", 3), ("PUSH", 1)]
    lines = disassemble(prog)
    assert lines == ["   0  PUSH          0", "   1  JUMP_IF_FALSE L1", "   2  PUSH          1", "L1:"], (
        "A target equal to len(program) means 'the end': put its label line after the last instruction."
    )


def test_label_on_first_instruction():
    prog = [("PUSH", 1), ("JUMP", 0)]
    assert disassemble(prog)[0] == "L1:", "A target 0 gets its label line before the very first instruction."


def test_call_operand():
    prog = [("PUSH", 2), ("PUSH", 3), ("CALL", (4, 2)), ("HALT", None), ("ADD", None), ("RET", None)]
    assert disassemble(prog)[2] == "   2  CALL          L1 2", "CALL shows its label, a space, then nargs."


def test_empty_program():
    assert disassemble([]) == [], "An empty program has an empty listing."


@pytest.mark.parametrize("prog, why", [
    ([("PUSH", 1), ("FLY", None)], "an unknown op"),
    ([("JUMP", 5)], "a jump target past len(program)"),
    ([("JUMP", -1)], "a negative jump target"),
    ([("CALL", (9, 0))], "a CALL target past len(program)"),
])
def test_bad_programs(prog, why):
    with pytest.raises(ValueError):
        disassemble(prog)
    with pytest.raises(ValueError):
        jump_targets(prog)


# ------------------------------------------------------------------ to_assembly
def test_to_assembly_text():
    text = to_assembly([("PUSH", 0), ("JUMP_IF_FALSE", 3), ("CALL", (3, 0)), ("RET", None)])
    assert text == "    PUSH 0\n    JUMP_IF_FALSE L1\n    CALL L1 0\nL1:\n    RET\n", (
        "to_assembly: label lines 'Lk:' at the left, each instruction indented by 4 spaces as 'OP operand', "
        "every line ending with a newline."
    )


def test_to_assembly_round_trip():
    assert mini_assemble(to_assembly(SQUARES)) == SQUARES, (
        "Assembling the text from to_assembly must give back exactly the same program."
    )


def test_to_assembly_round_trip_label_at_end():
    prog = [("PUSH", 0), ("JUMP_IF_FALSE", 3), ("PUSH", 1)]
    assert mini_assemble(to_assembly(prog)) == prog, "Do not forget the label that points at the end."


def test_listing_and_assembly_use_same_labels():
    listing = disassemble(SQUARES)
    text = to_assembly(SQUARES)
    labels_in_listing = [line for line in listing if line.endswith(":")]
    labels_in_text = [line for line in text.splitlines() if line.endswith(":")]
    assert labels_in_listing == labels_in_text == ["L1:", "L2:", "L3:"], (
        "Both functions should share one label-naming helper so they never disagree."
    )
