import dis
import types
from collections import Counter

from solution import by_prefix, opcode_histogram


# The tests never compare against a fixed listing: opnames differ between 3.11 and 3.14.
# They check properties that hold on every version.


def area(w, h):
    return w * h


def count_up(n):
    total = 0
    for i in range(n):
        total += i
    return total


def outer():
    def inner(x):
        return x + 1
    return inner


def two_levels():
    def middle():
        square = lambda y: y * y
        return square
    return middle


def code_objects(code):
    """Every code object reachable through co_consts, including code itself."""
    found = [code]
    for const in code.co_consts:
        if isinstance(const, types.CodeType):
            found += code_objects(const)
    return found


def n_instructions(code):
    return len(list(dis.get_instructions(code)))


def test_returns_a_counter_of_opnames():
    hist = opcode_histogram(area)
    assert isinstance(hist, Counter), "Return a collections.Counter, not a plain dict or list."
    assert hist.total() > 0, "Every function has instructions; did you forget to count them?"
    assert all(isinstance(k, str) and k.isupper() for k in hist), (
        "Keys must be opnames like 'LOAD_FAST' (Instruction.opname), not Instruction objects or numbers."
    )


def test_total_matches_get_instructions():
    for f in (area, count_up, outer):
        assert opcode_histogram(f).total() == n_instructions(f), (
            f"For {f.__name__} the counts must add up to the number of instructions from "
            "dis.get_instructions(f) (default arguments, so CACHE entries are not included)."
        )


def test_counts_match_each_opname():
    expected = Counter(i.opname for i in dis.get_instructions(count_up))
    assert opcode_histogram(count_up) == expected, "Each opname must be counted as many times as it appears."


def test_stable_properties():
    hist = opcode_histogram(count_up)
    assert any(name.startswith("LOAD") for name in hist), "A function always loads values: expect some LOAD_... opname."
    assert any("JUMP" in name for name in hist), (
        "A for loop jumps back to its start: some opname containing 'JUMP' must be counted."
    )
    assert not any("JUMP" in name for name in opcode_histogram(area)), (
        "area() has no if and no loop, so it has no jump. Are you counting another function's code?"
    )


def test_accepts_a_code_object():
    assert opcode_histogram(area.__code__) == opcode_histogram(area), (
        "opcode_histogram must accept a code object too (dis.get_instructions does)."
    )


def test_not_recursive_by_default():
    assert opcode_histogram(outer).total() == n_instructions(outer), (
        "Without recursive=True, count only outer's own instructions, not inner's."
    )


def test_recursive_adds_nested_code():
    inner_code = [c for c in outer.__code__.co_consts if isinstance(c, types.CodeType)][0]
    expected = n_instructions(outer) + n_instructions(inner_code)
    got = opcode_histogram(outer, recursive=True).total()
    assert got == expected, (
        f"Expected {expected} instructions (outer + inner), got {got}. The inner function's code object "
        "is a constant in outer.__code__.co_consts: count its instructions too."
    )


def test_recursive_goes_to_any_depth():
    expected = sum(n_instructions(c) for c in code_objects(two_levels.__code__))
    got = opcode_histogram(two_levels, recursive=True).total()
    assert got == expected, (
        f"Expected {expected}, got {got}. two_levels contains middle, which contains a lambda: "
        "walk co_consts again inside every nested code object (recursion)."
    )
    assert opcode_histogram(two_levels, recursive=True) >= opcode_histogram(two_levels), (
        "The recursive histogram includes everything the flat one has."
    )


def test_recursive_on_function_without_nested_code():
    assert opcode_histogram(area, recursive=True) == opcode_histogram(area), (
        "A function with no nested code objects gives the same histogram either way."
    )


def test_by_prefix():
    hist = Counter({"LOAD_FAST": 3, "LOAD_CONST": 1, "RETURN_VALUE": 1, "RESUME": 1})
    assert by_prefix(hist) == Counter({"LOAD": 4, "RETURN": 1, "RESUME": 1}), (
        "Group by the text before the FIRST underscore, add the counts, keep names without '_' as they are."
    )
    assert isinstance(by_prefix(hist), Counter), "by_prefix must return a Counter."


def test_by_prefix_splits_at_first_underscore_only():
    hist = Counter({"POP_JUMP_IF_FALSE": 2, "JUMP_BACKWARD": 1})
    assert by_prefix(hist) == Counter({"POP": 2, "JUMP": 1}), (
        "'POP_JUMP_IF_FALSE' belongs to 'POP' (first underscore), not 'JUMP' or 'POP_JUMP_IF'."
    )


def test_by_prefix_does_not_change_input():
    hist = Counter({"LOAD_FAST": 2})
    by_prefix(hist)
    assert hist == Counter({"LOAD_FAST": 2}), "Build a new Counter; do not modify the one you were given."


def test_by_prefix_on_real_function():
    hist = opcode_histogram(count_up)
    grouped = by_prefix(hist)
    assert grouped.total() == hist.total(), "Grouping must keep the total number of instructions."
    assert grouped["LOAD"] > 0, "count_up loads values, so the 'LOAD' group cannot be empty."
