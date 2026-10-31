import pytest

from solution import shrink


class Budget:
    """Wraps a fails() function: counts calls, checks the argument, stops runaway searches."""

    def __init__(self, fails, limit=20_000):
        self.fails = fails
        self.limit = limit
        self.calls = 0

    def __call__(self, candidate):
        assert isinstance(candidate, list), f"Pass fails() a list, got {type(candidate).__name__}."
        self.calls += 1
        if self.calls > self.limit:
            raise AssertionError(
                f"More than {self.limit} calls of fails(). Do not try every subset; remove one "
                "element (or one chunk) at a time and keep the removal when it still fails."
            )
        return self.fails(list(candidate))


def is_subsequence(small, big):
    it = iter(big)
    return all(any(x == y for y in it) for x in small)


def check_rules(items, fails, result):
    assert isinstance(result, list), f"Return a list, got {type(result).__name__}."
    assert fails(list(result)), f"{result!r} does not fail any more. Only keep a removal when fails() is still True."
    assert is_subsequence(result, items), (
        f"{result!r} is not a subsequence of the input: only remove elements, keep the order."
    )
    for i in range(len(result)):
        smaller = result[:i] + result[i + 1:]
        assert not fails(smaller), (
            f"{result!r} is not 1-minimal: removing element {i} ({result[i]!r}) still fails. "
            "Keep looping until a full pass removes nothing."
        )


def test_two_lines_matter():
    source = ["# demo", "import os", "import x", "print(1)", "x.run()", "print(2)"]

    def fails(lines):
        return "import x" in lines and "x.run()" in lines

    assert shrink(source, Budget(fails)) == ["import x", "x.run()"], (
        "Only 'import x' and 'x.run()' are needed for the failure; everything else can go."
    )


def test_numbers_three_and_seven():
    def fails(s):
        return 3 in s and 7 in s

    assert shrink(list(range(1, 11)), Budget(fails)) == [3, 7], "Only 3 and 7 are needed."


def test_sum_threshold_has_many_answers():
    items = [5, 1, 4, 2, 8, 3]

    def fails(s):
        return sum(s) >= 15

    check_rules(items, fails, shrink(items, Budget(fails)))


def test_non_monotone_failure():
    items = [1, 0, 0, 1, 0, 2, 1, 1]

    def fails(s):
        return s.count(1) % 2 == 0 and s.count(1) > 0 and 2 in s

    # Removing one '1' makes it pass, but removing two makes it fail again.
    result = shrink(items, Budget(fails))
    check_rules(items, fails, result)


def test_duplicates_are_separate_elements():
    def fails(s):
        return s.count("x") >= 2

    assert shrink(["x", "x", "x", "x"], Budget(fails)) == ["x", "x"], (
        "Equal elements are still separate positions: remove by index, not with list.remove(value)."
    )


def test_one_pass_is_not_enough():
    def fails(s):
        return s in (["a", "b", "c"], ["a", "c"], ["c"])

    # Removing "a" first does not fail; only after "b" is gone can "a" go too.
    assert shrink(["a", "b", "c"], Budget(fails)) == ["c"], (
        "After ['a', 'c'] is reached, removing 'a' still fails, so ['a', 'c'] is not 1-minimal. "
        "Repeat passes until a whole pass removes nothing."
    )


def test_remove_by_position_not_by_value():
    items = [1, 2, 1]

    def fails(s):
        return s[:1] == [1] and 2 in s

    assert shrink(items, Budget(fails)) == [1, 2], (
        "Only the LAST 1 can go. list.remove(1) always removes the first 1, so it never tries "
        "the right one: build candidates by position, current[:i] + current[i + 1:]."
    )


def test_everything_removable():
    assert shrink([1, 2, 3], Budget(lambda s: True)) == [], (
        "If fails() is always True, everything can be removed: return []."
    )
    assert shrink([], Budget(lambda s: True)) == [], "An empty failing input shrinks to []."


def test_not_failing_raises():
    with pytest.raises(ValueError):
        shrink([1, 2, 3], Budget(lambda s: False))


def test_input_not_changed():
    items = [4, 8, 15, 16, 23, 42]
    before = list(items)
    shrink(items, Budget(lambda s: 15 in s))
    assert items == before, "Do not change the caller's list; work on a copy."


def test_large_input_within_budget():
    items = list(range(300))
    needed = {17, 150, 299}

    def fails(s):
        return needed <= set(s)

    budget = Budget(fails)
    assert shrink(items, budget) == [17, 150, 299], "Only 17, 150 and 299 are needed."


def test_large_input_with_order_dependent_failure():
    items = ["a", "<", "b"] * 40 + [">", "c"] * 40

    def fails(s):
        return "<" in s and ">" in s[s.index("<"):]

    result = shrink(items, Budget(fails))
    assert result == ["<", ">"], f"Expected ['<', '>'], got {result!r}."
