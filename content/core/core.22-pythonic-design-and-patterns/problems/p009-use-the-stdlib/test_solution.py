import ast
from pathlib import Path

import solution
from solution import (bfs_order, count_paths, group_by_length, join_all, run_lengths,
                      top_words, word_counts)

TREE = ast.parse(Path(solution.__file__).read_text())
TEXT = "the cat and the hat and The bat"


def _func(name):
    for node in ast.walk(TREE):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    raise AssertionError(f"function {name} is missing")


def _names(node):
    out = set()
    for n in ast.walk(node):
        if isinstance(n, ast.Name):
            out.add(n.id)
        elif isinstance(n, ast.Attribute):
            out.add(n.attr)
    return out


def _no_for(name):
    loops = [n for n in ast.walk(_func(name)) if isinstance(n, (ast.For, ast.While))]
    assert not loops, f"{name} still has a for/while statement; the standard library does this in one call."


def test_word_counts():
    assert word_counts(TEXT) == {"the": 3, "cat": 1, "and": 2, "hat": 1, "bat": 1}, "Case is ignored: 'The' and 'the' are one word."
    assert word_counts("") == {}, "No words: empty."


def test_top_words():
    assert top_words(TEXT, 2) == [("the", 3), ("and", 2)], "Most common first, as (word, count) pairs."
    assert top_words(TEXT, 4) == [("the", 3), ("and", 2), ("cat", 1), ("hat", 1)], "Ties keep first-seen order (cat before hat before bat)."
    assert top_words("", 3) == [], "No words: empty list."
    assert top_words("a b", 10) == [("a", 1), ("b", 1)], "Asking for more than exist is fine."


def test_group_by_length():
    assert group_by_length(["a", "bb", "c", "dd", "eee"]) == {1: ["a", "c"], 2: ["bb", "dd"], 3: ["eee"]}, "Group by len(word), keep the input order."
    assert group_by_length([]) == {}, "No words: empty dict."


def test_bfs_order():
    g = {"a": ["b", "c"], "b": ["d"], "c": ["d", "e"], "d": ["a"], "e": []}
    assert bfs_order(g, "a") == ["a", "b", "c", "d", "e"], "Breadth first: neighbours before neighbours of neighbours; no repeats."
    assert bfs_order(g, "e") == ["e"], "A node with no neighbours."
    assert bfs_order({}, "z") == ["z"], "Unknown start node: just itself."


def test_bfs_order_big_graph():
    n = 3000
    g = {i: [i + 1] for i in range(n)}
    assert bfs_order(g, 0) == list(range(n + 1)), "A long chain of 3000 nodes."


def test_run_lengths():
    assert run_lengths("aaabcc") == [("a", 3), ("b", 1), ("c", 2)], "Count each run of equal neighbours."
    assert run_lengths("") == [], "Empty input."
    assert run_lengths([1, 1, 2, 1]) == [(1, 2), (2, 1), (1, 1)], "A repeated value in a later run is a NEW run."


def test_join_all():
    assert join_all([1, 2], [3], []) == [1, 2, 3], "All items in order."
    assert join_all() == [], "No lists: empty."
    assert join_all("ab", (1,)) == ["a", "b", 1], "Any iterables work; the result is a list."


def test_count_paths():
    assert [count_paths(n) for n in range(6)] == [1, 1, 2, 3, 5, 8], "Fibonacci-like: 1 1 2 3 5 8."
    assert count_paths(30) == 1346269, "Value for 30 stairs."


def test_stdlib_tools_are_used():
    assert "Counter" in _names(_func("word_counts")), "word_counts: use collections.Counter."
    assert "defaultdict" in _names(_func("group_by_length")), "group_by_length: use collections.defaultdict(list)."
    assert "deque" in _names(_func("bfs_order")), "bfs_order: use collections.deque as the queue."
    assert "groupby" in _names(_func("run_lengths")), "run_lengths: use itertools.groupby."
    assert "chain" in _names(_func("join_all")), "join_all: use itertools.chain."
    decorators = set()
    for d in _func("count_paths").decorator_list:
        decorators |= _names(d)
    assert decorators & {"cache", "lru_cache"}, "count_paths: add @functools.cache so each n is computed once."


def test_no_hand_written_loops_or_checks():
    for name in ("word_counts", "top_words", "run_lengths", "join_all"):
        _no_for(name)
    for node in ast.walk(_func("group_by_length")):
        if isinstance(node, ast.Compare) and any(isinstance(o, (ast.In, ast.NotIn)) for o in node.ops):
            raise AssertionError("group_by_length still checks 'in' before appending; defaultdict(list) creates the list for you.")
    for node in ast.walk(_func("bfs_order")):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "pop" \
                and node.args and isinstance(node.args[0], ast.Constant) and node.args[0].value == 0:
            raise AssertionError("list.pop(0) moves every item (O(n) each time). Use deque.popleft().")
