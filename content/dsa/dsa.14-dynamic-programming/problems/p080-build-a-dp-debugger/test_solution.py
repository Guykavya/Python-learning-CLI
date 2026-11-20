import pytest

from solution import CyclicState, DPError, MissingBaseCase, dp_debug

INF = float("inf")


def make_fib():
    @dp_debug
    def fib(n):
        return n if n < 2 else fib(n - 1) + fib(n - 2)
    return fib


def test_fib_value_and_table():
    fib = make_fib()
    assert fib(30) == 832040, "fib(30) should be 832040: the wrapper must return the function's value."
    assert hasattr(fib, "table"), "The wrapper needs a .table attribute (a dict state -> value)."
    assert len(fib.table) == 31, f"fib(30) computes the 31 states 0..30, the table has {len(fib.table)}."
    assert fib.table[(10,)] == 55, "Keys are argument tuples: fib.table[(10,)] should be 55."
    assert list(fib.table)[:3] == [(1,), (0,), (2,)], (
        f"States go into the table when they FINISH: (1,), (0,), (2,) first; got {list(fib.table)[:3]}.")
    assert list(fib.table)[-1] == (30,), "The first call finishes last: (30,) is the last key."


def test_fib_counters():
    fib = make_fib()
    fib(30)
    assert (fib.calls, fib.hits) == (59, 28), (
        f"fib(30): expected 59 calls (1 + 2 per state from 2 to 30) and 28 hits (59 - 31 computed); got "
        f"calls={fib.calls}, hits={fib.hits}. Count every call, including memo hits.")
    assert fib.deepest == 30, (
        f"fib(30) goes 30 states deep (fib(30) -> ... -> fib(1)) before anything finishes; got {fib.deepest}.")
    fib(30)
    assert (fib.calls, fib.hits) == (60, 29), "A second fib(30) is one more call, and it is a hit."


def test_name_is_kept():
    fib = make_fib()
    assert fib.__name__ == "fib", "Use functools.wraps so the wrapper keeps the name 'fib'."


def test_reset():
    fib = make_fib()
    fib(20)
    fib.reset()
    assert (fib.table, fib.calls, fib.hits, fib.deepest) == ({}, 0, 0, 0), (
        "reset() must empty the table and set calls, hits and deepest back to 0.")
    assert fib(10) == 55 and fib.calls == 19, "After reset(), fib(10) is computed again: 19 calls."


def test_coin_change():
    @dp_debug
    def fewest(a):
        if a == 0:
            return 0
        return min((fewest(a - c) + 1 for c in (1, 3, 4) if c <= a), default=INF)

    assert fewest(6) == 2, "Fewest coins from (1, 3, 4) for 6 is 2 (3 + 3)."
    want = {(0,): 0, (1,): 1, (2,): 2, (3,): 1, (4,): 1, (5,): 2, (6,): 2}
    assert fewest.table == want, f"Expected the table {want}, got {fewest.table}."
    assert (fewest.calls, fewest.hits) == (14, 7), (
        f"Expected 14 calls and 7 hits, got calls={fewest.calls}, hits={fewest.hits}.")


def test_two_arguments():
    @dp_debug
    def paths(r, c):
        if r == 0 or c == 0:
            return 1
        return paths(r - 1, c) + paths(r, c - 1)

    assert paths(3, 3) == 20, "paths(3, 3) = comb(6, 3) = 20."
    assert (2, 1) in paths.table and paths.table[(2, 1)] == 3, (
        "With two arguments the state is the tuple (r, c): paths.table[(2, 1)] should be 3.")
    assert (len(paths.table), paths.calls, paths.hits) == (15, 19, 4), (
        f"Expected 15 states, 19 calls, 4 hits; got {len(paths.table)}, {paths.calls}, {paths.hits}.")


def test_missing_base_case():
    @dp_debug
    def bad(n):
        return bad(n - 1) + 1

    with pytest.raises(MissingBaseCase) as info:
        bad(0)
    assert "bad(-200)" in str(info.value), (
        f"The message should name the state that went past the depth limit, bad(-200); got: {info.value}")
    assert isinstance(info.value, DPError), "MissingBaseCase must stay a subclass of DPError."
    assert bad.table == {}, "Nothing finished, so nothing may be stored in the table."


def test_not_a_recursion_error():
    @dp_debug
    def down(n):
        return down(n - 1)

    try:
        down(5)
    except MissingBaseCase:
        pass
    except RecursionError:
        assert False, (
            "Got Python's RecursionError: raise MissingBaseCase as soon as max_depth (200) states are in progress.")


def test_custom_depth_and_cleanup():
    @dp_debug(max_depth=50)
    def countdown(n):
        return 0 if n == 0 else countdown(n - 1)

    with pytest.raises(MissingBaseCase) as info:
        countdown(60)
    assert "countdown(10)" in str(info.value), (
        f"With max_depth=50, countdown(60) fails at the 51st state, countdown(10); got: {info.value}")
    assert countdown(49) == 0, (
        "After the error, countdown(49) (exactly 50 states deep) must work. If it fails at once, the states "
        "of the failed call are still marked 'in progress': pop them in a finally: block.")
    assert countdown.deepest == 50, f"deepest should be 50, got {countdown.deepest}."


def test_cycle():
    @dp_debug
    def spin(n):
        return spin(n % 3 + 1)

    with pytest.raises(CyclicState) as info:
        spin(1)
    assert "spin(1) -> spin(2) -> spin(3) -> spin(1)" in str(info.value), (
        f"The message should show the cycle 'spin(1) -> spin(2) -> spin(3) -> spin(1)'; got: {info.value}")
    with pytest.raises(CyclicState) as info:
        spin(2)
    assert "spin(2) -> spin(3) -> spin(1) -> spin(2)" in str(info.value), (
        f"A second call must start from a clean stack: expected the cycle from spin(2); got: {info.value}")


def test_self_cycle_is_not_a_depth_error():
    @dp_debug
    def same(n):
        return same(n) + 1

    with pytest.raises(CyclicState) as info:
        same(7)
    assert "same(7) -> same(7)" in str(info.value), (
        f"same(7) needs same(7): report the cycle 'same(7) -> same(7)', got: {info.value}")


def test_other_errors_pass_through():
    @dp_debug
    def fragile(n):
        if n == 3:
            raise ValueError("bad input 3")
        return 0 if n == 0 else fragile(n - 1)

    with pytest.raises(ValueError):
        fragile(5)
    assert fragile(2) == 0, "After a ValueError inside the function, the debugger must still work (stack cleared)."
    with pytest.raises(ValueError):
        fragile(4)
