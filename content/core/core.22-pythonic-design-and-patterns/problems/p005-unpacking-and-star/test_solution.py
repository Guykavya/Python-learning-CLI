import ast
from pathlib import Path

import solution
from solution import (describe_point, distance_between, fib, merge_settings,
                      split_head_tail, swap_pairs, trim_ends)

TREE = ast.parse(Path(solution.__file__).read_text())
INDEX_FUNCS = ("describe_point", "split_head_tail", "trim_ends", "swap_pairs", "distance_between")


def _func(name):
    for node in ast.walk(TREE):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    raise AssertionError(f"function {name} is missing")


def test_describe_point():
    assert describe_point((1, 2, 3)) == "x=1, y=2, z=3", "Format is 'x=1, y=2, z=3'."
    assert describe_point([0, -1, 2.5]) == "x=0, y=-1, z=2.5", "A list of three works too."


def test_split_head_tail():
    assert split_head_tail([1, 2, 3]) == (1, [2, 3]), "First item, then a LIST of the rest."
    assert split_head_tail([7]) == (7, []), "One item: the rest is an empty list."
    assert split_head_tail([]) == (None, []), "Empty input gives (None, [])."
    assert split_head_tail("abc") == ("a", ["b", "c"]), "The rest is always a list (a starred name is a list)."
    assert split_head_tail((1, 2)) == (1, [2]), "A tuple works too; the rest is still a list."


def test_trim_ends():
    assert trim_ends([1, 2, 3, 4]) == [2, 3], "Drop the first and the last item."
    assert trim_ends([1, 2]) == [], "Two items: nothing left."
    assert trim_ends([1]) == [], "One item: [] (not an error)."
    assert trim_ends([]) == [], "Empty: []."
    assert trim_ends((1, 2, 3)) == [2], "A tuple input still gives a list."


def test_swap_pairs():
    assert swap_pairs([(1, "a"), (2, "b")]) == [("a", 1), ("b", 2)], "Each pair is reversed."
    assert swap_pairs([]) == [], "Empty gives empty."
    assert swap_pairs([[1, 2]]) == [(2, 1)], "Output items are tuples."


def test_distance_between():
    assert distance_between(((0, 0), (3, 4))) == 5.0, "3-4-5 triangle."
    assert distance_between(((1, 1), (1, 1))) == 0.0, "Same point: 0."
    assert distance_between(((-1, -1), (2, 3))) == 5.0, "Negative coordinates work."


def test_fib():
    assert [fib(n) for n in range(8)] == [0, 1, 1, 2, 3, 5, 8, 13], "Sequence 0 1 1 2 3 5 8 13."
    assert fib(50) == 12586269025, "Large n: the two names must update together (a, b = b, a + b)."


def test_merge_settings():
    d, u, o = {"a": 1, "b": 1}, {"b": 2, "c": 2}, {"c": 3, "d": 3}
    assert merge_settings(d, u, o) == {"a": 1, "b": 2, "c": 3, "d": 3}, "Later dicts win: overrides over user over defaults."
    assert d == {"a": 1, "b": 1} and u == {"b": 2, "c": 2} and o == {"c": 3, "d": 3}, "Inputs must not change."
    assert merge_settings({}, {}, {}) == {}, "Empty dicts merge to {}."
    assert list(merge_settings({"x": 1}, {"y": 2}, {})) == ["x", "y"], "Keep insertion order: defaults first."


def _is_number_index(sub):
    s = sub.slice
    if isinstance(s, ast.Constant) and isinstance(s.value, int):
        return True
    return isinstance(s, ast.UnaryOp) and isinstance(s.operand, ast.Constant) and isinstance(s.operand.value, int)


def test_no_numeric_subscripts():
    for name in INDEX_FUNCS:
        for node in ast.walk(_func(name)):
            if isinstance(node, ast.Subscript) and _is_number_index(node):
                raise AssertionError(
                    f"{name} uses a numeric index like x[0] or x[-1]. Unpack instead: "
                    "'x, y = p', 'first, *rest = items', '(x1, y1), (x2, y2) = segment'."
                )


def test_star_is_used():
    for name in ("split_head_tail", "trim_ends"):
        assert any(isinstance(n, ast.Starred) for n in ast.walk(_func(name))), (
            f"{name} should use starred unpacking: 'first, *rest = items' / '_, *middle, _ = items'."
        )


def test_fib_swaps_in_one_statement():
    ok = any(isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Tuple) and isinstance(n.value, ast.Tuple)
             for n in ast.walk(_func("fib")))
    assert ok, "fib should update both names at once: 'a, b = b, a + b' (no temporary variable)."


def test_merge_uses_pipe_or_double_star():
    f = _func("merge_settings")
    pipe = any(isinstance(n, ast.BinOp) and isinstance(n.op, ast.BitOr) for n in ast.walk(f))
    stars = any(isinstance(n, ast.Dict) and None in n.keys for n in ast.walk(f))
    assert pipe or stars, "merge_settings should use 'defaults | user | overrides' or {**defaults, **user, **overrides}."
