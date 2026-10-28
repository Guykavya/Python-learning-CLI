import itertools

from solution import counted, drain


def gen_with_return():
    yield 1
    yield 2
    return "done"


def gen_return_falsy():
    yield "a"
    return 0


def test_drain_reads_return_value():
    assert drain(gen_with_return()) == ([1, 2], "done"), (
        "Catch StopIteration as e and use e.value. list() and for loops lose the return value."
    )


def test_drain_falsy_return_value():
    assert drain(gen_return_falsy()) == (["a"], 0), "A return value of 0 must come back as 0, not None."


def test_drain_plain_iterator():
    assert drain(iter([7, 8])) == ([7, 8], None), "A plain iterator has no return value: the result is None."


def test_counted_yields_unchanged():
    assert list(counted("abc")) == ["a", "b", "c"], "counted must yield every item unchanged."


def test_counted_returns_count():
    assert drain(counted("abc")) == (["a", "b", "c"], 3), "counted must 'return n' after the loop, where n is the number of items."
    assert drain(counted([])) == ([], 0), "An empty input: return 0, not None. Start the counter at 0 and always return it."


def test_counted_with_yield_from():
    def report():
        n = yield from counted(["x", "y"])
        yield f"total {n}"
        return "ok"

    assert drain(report()) == (["x", "y", "total 2"], "ok"), (
        "yield from counted(...) must evaluate to the count. Did counted 'return' the number?"
    )


def test_counted_is_lazy():
    g = counted(itertools.count(10))
    assert next(g) == 10, "counted must be a lazy generator: it must work on an infinite input."
    assert next(g) == 11, "counted must yield the items one by one."


def test_counted_one_pass():
    source = iter([1, 2, 3])
    assert drain(counted(source)) == ([1, 2, 3], 3), "counted must read the input only once (it may be an iterator)."
