import ast
from pathlib import Path

import solution
from solution import (any_big, count_long, first_duplicate, flatten, log_and_double,
                      pythagorean_triples, squares_of_evens, word_lengths)

TREE = ast.parse(Path(solution.__file__).read_text())
COMPS = (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)


class Counting:
    """An iterable that counts how many items were taken from it."""

    def __init__(self, data):
        self.data = data
        self.taken = 0

    def __iter__(self):
        for x in self.data:
            self.taken += 1
            yield x


def _func(name):
    for node in ast.walk(TREE):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    raise AssertionError(f"function {name} is missing")


def _has(name, kinds):
    return any(isinstance(n, kinds) for n in ast.walk(_func(name)))


def test_squares_of_evens():
    assert squares_of_evens([1, 2, 3, 4, -2]) == [4, 16, 4], "Square the even numbers only, keep the order (-2 is even)."
    assert squares_of_evens([]) == [], "Empty gives empty."


def test_word_lengths():
    assert word_lengths("the quick fox") == {"the": 3, "quick": 5, "fox": 3}, "Map each word to its length."
    assert word_lengths("") == {}, "No words: empty dict."
    assert word_lengths("a a bb") == {"a": 1, "bb": 2}, "A repeated word is one key."


def test_count_long():
    assert count_long(["a", "abc", "abcd", "abcde"], 3) == 2, "Longer than 3 letters: abcd, abcde."
    assert count_long([], 3) == 0, "No words: 0."
    assert count_long((w for w in ["xxxx", "y"]), 1) == 1, "A generator can be read only once: do not read it twice."


def test_any_big_is_lazy():
    stream = Counting(range(1_000_000))
    assert any_big(stream, 4) is True, "5 is bigger than 4."
    assert stream.taken <= 6, (
        f"any_big read {stream.taken} items. It must stop at the first big one. "
        "any(x > limit for x in items) is lazy; a list comprehension reads everything first."
    )
    assert any_big([1, 2], 5) is False, "No item above the limit."
    assert any_big([], 0) is False, "No items: False."


def test_flatten():
    assert flatten([[1, 2], [3], []]) == [1, 2, 3], "Join the rows in order; empty rows vanish."
    assert flatten([]) == [], "No rows: empty."


def test_pythagorean_triples():
    assert pythagorean_triples(20) == [(3, 4, 5), (5, 12, 13), (6, 8, 10), (8, 15, 17), (9, 12, 15), (12, 16, 20)], (
        "Ascending order by a, then b. Triples need c <= n."
    )
    assert pythagorean_triples(4) == [], "No triple fits in 4."
    assert len(pythagorean_triples(100)) == 52, "There are 52 triples with c <= 100."


def test_log_and_double_keeps_the_side_effects():
    seen = []
    assert log_and_double([1, 2, 3], seen.append) == [2, 4, 6], "Return the doubled items."
    assert seen == [1, 2, 3], "log must be called once per item, in order."
    seen2 = []
    assert log_and_double([], seen2.append) == [], "No items: no calls."
    assert seen2 == [], "No items: log is never called."


def test_first_duplicate_stops_early():
    stream = Counting([1, 2, 3, 2, 9, 9, 9, 9])
    assert first_duplicate(stream) == 2, "2 is the first value to appear a second time."
    assert stream.taken == 4, (
        f"first_duplicate read {stream.taken} items; it must stop after reading the second 2 (4 items). "
        "An early exit needs a loop with return."
    )
    assert first_duplicate([1, 2, 3]) is None, "No duplicates: None."
    assert first_duplicate([5, 5, 1, 1]) == 5, "The first value that REPEATS, not the most frequent."


def test_comprehensions_where_they_fit():
    assert _has("squares_of_evens", ast.ListComp), "squares_of_evens: a list comprehension fits (build a list from a list)."
    assert _has("word_lengths", ast.DictComp), "word_lengths: a dict comprehension fits."
    for name in ("squares_of_evens", "word_lengths", "count_long", "any_big", "flatten"):
        loops = [n for n in ast.walk(_func(name)) if isinstance(n, (ast.For, ast.While))]
        assert not loops, f"{name} still has a for/while statement; a comprehension or any/sum expresses it directly."


def test_no_list_built_just_to_be_consumed():
    for name in ("count_long", "any_big"):
        assert not _has(name, ast.ListComp), (
            f"{name} builds a whole list in square brackets only to count or test it. "
            "Use a generator expression (round brackets) inside sum() / any()."
        )


def test_loops_stay_loops():
    for name in ("log_and_double", "first_duplicate"):
        assert _has(name, ast.For), f"{name} needs its for loop (side effects / early exit); do not force a comprehension."
    for node in ast.walk(_func("log_and_double")):
        if isinstance(node, COMPS):
            for call in ast.walk(node):
                if isinstance(call, ast.Call) and isinstance(call.func, ast.Name) and call.func.id == "log":
                    raise AssertionError("log() is called inside a comprehension. A comprehension is for building values, not for side effects: use a loop.")


def test_comprehension_depth():
    for node in ast.walk(TREE):
        if isinstance(node, COMPS):
            assert len(node.generators) <= 2, (
                "A comprehension has 3 'for' clauses. Past two, it is unreadable: "
                "use a loop or split it into a helper."
            )
