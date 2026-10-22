import ast
import inspect
import solution
from solution import for_each


def test_no_for_loop():
    tree = ast.parse(inspect.getsource(solution))
    bad = [n for n in ast.walk(tree) if isinstance(n, (ast.For, ast.comprehension, ast.GeneratorExp))]
    assert not bad, "for_each must not use a for loop or a comprehension. Use iter(), next() and try/except StopIteration."


def test_calls_action_in_order_and_counts():
    seen = []
    assert for_each([5, 6, 7], seen.append) == 3, "Return the number of items handled."
    assert seen == [5, 6, 7], "Call action(item) for every item, in order."


def test_string_and_empty():
    seen = []
    assert for_each("ab", seen.append) == 2, "A string is iterable too."
    assert seen == ["a", "b"], "Items of a string are its characters."
    assert for_each([], seen.append) == 0, "An empty iterable gives 0."


def test_generator_input():
    seen = []
    assert for_each((n * 2 for n in range(3)), seen.append) == 3, "Generators have no len(): count while you loop."
    assert seen == [0, 2, 4], "Items come from the generator in order."


def test_continues_a_partly_used_iterator():
    it = iter([1, 2, 3, 4])
    next(it)
    seen = []
    assert for_each(it, seen.append) == 3, "iter(it) is it: continue from the current position."
    assert seen == [2, 3, 4], "The first item was already taken, so it must not appear."
    assert list(it) == [], "for_each must use up the iterator."


def test_calls_iter_only_once():
    class Once:
        calls = 0

    data = [1, 2, 3]
    seen = []

    def action(x):
        seen.append(x)
        assert len(seen) <= 3, "Looping forever: call iter() once, before the loop, not inside it."

    assert for_each(data, action) == 3, "Three items, three calls."
