import re

import pytest

from solution import StackUnderflow, max_depth, simulate


def test_push_and_add():
    assert simulate([("PUSH", 2), ("PUSH", 3), ("ADD", None)]) == [5], "PUSH 2, PUSH 3, ADD leaves [5]."


def test_expression():
    prog = [("PUSH", 2), ("PUSH", 3), ("ADD", None), ("PUSH", 4), ("MUL", None)]
    assert simulate(prog) == [20], "(2 + 3) * 4 = 20: ADD's result stays on the stack for MUL."


def test_dup():
    assert simulate([("PUSH", 7), ("DUP", None), ("MUL", None)]) == [49], "DUP copies the top value, so 7 * 7."


def test_swap_order():
    assert simulate([("PUSH", 1), ("PUSH", 2), ("SWAP", None)]) == [2, 1], (
        "SWAP exchanges the top two values; the result is returned bottom first."
    )


def test_pop():
    assert simulate([("PUSH", 1), ("PUSH", 2), ("POP", None)]) == [1], "POP removes the TOP value (the 2)."


def test_leftover_values_bottom_first():
    assert simulate([("PUSH", 1), ("PUSH", 2), ("PUSH", 3)]) == [1, 2, 3], "Return the stack bottom first, like a list you append to."


def test_empty_program():
    assert simulate([]) == [], "An empty program leaves an empty stack."
    assert max_depth([]) == 0, "An empty program never puts anything on the stack."


def check_underflow(prog, offset):
    with pytest.raises(StackUnderflow) as info:
        simulate(prog)
    assert re.search(rf"\boffset {offset}\b", str(info.value)), (
        f"The StackUnderflow message must contain 'offset {offset}' (the index of the failing instruction)."
    )


def test_underflow_reports_offset():
    check_underflow([("PUSH", 1), ("ADD", None)], 1)
    check_underflow([("POP", None)], 0)
    check_underflow([("DUP", None)], 0)
    check_underflow([("PUSH", 1), ("PUSH", 2), ("MUL", None), ("SWAP", None)], 3)


def test_underflow_is_not_index_error():
    with pytest.raises(StackUnderflow):
        simulate([("PUSH", 5), ("SWAP", None)])
    try:
        simulate([("ADD", None)])
    except IndexError:
        pytest.fail("Check the stack depth yourself and raise StackUnderflow; do not let list.pop raise IndexError.")
    except StackUnderflow:
        pass


def test_unknown_op():
    with pytest.raises(ValueError) as info:
        simulate([("PUSH", 1), ("NOP", None)])
    assert "NOP" in str(info.value), "The ValueError message must name the unknown op."


def test_does_not_change_input():
    prog = [("PUSH", 1), ("PUSH", 2), ("ADD", None)]
    copy = list(prog)
    simulate(prog)
    assert prog == copy, "simulate must not modify the ops list."
    assert simulate(prog) == [3], "Calling simulate twice must give the same result: start from a new empty stack each time."


def test_max_depth():
    prog = [("PUSH", 2), ("PUSH", 3), ("ADD", None), ("PUSH", 4), ("MUL", None)]
    assert max_depth(prog) == 2, "The stack never holds more than 2 values here."
    deep = [("PUSH", 1), ("PUSH", 2), ("ADD", None), ("PUSH", 3), ("PUSH", 4), ("PUSH", 5)]
    assert max_depth(deep) == 4, "Count every push: 1, 2, then back to 1 after ADD, then 2, 3, 4."
    shrink = [("PUSH", 1), ("PUSH", 2), ("PUSH", 3), ("ADD", None), ("ADD", None)]
    assert max_depth(shrink) == 3, "max_depth is the LARGEST size seen (3), not the final size (1)."
    assert max_depth([("PUSH", 1), ("DUP", None), ("DUP", None)]) == 3, "Each DUP adds one value."


def test_max_depth_raises_too():
    with pytest.raises(StackUnderflow):
        max_depth([("ADD", None)])
