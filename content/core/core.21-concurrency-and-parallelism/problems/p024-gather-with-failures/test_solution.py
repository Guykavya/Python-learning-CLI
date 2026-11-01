import asyncio
import time

from solution import fetch_report


class BadId(Exception):
    pass


def make_fetch(plan):
    """plan: id -> (delay, value_or_exception). Records which fetches finished."""
    finished = []

    async def fetch(item_id):
        delay, outcome = plan[item_id]
        await asyncio.sleep(delay)
        finished.append(item_id)
        if isinstance(outcome, BaseException):
            raise outcome
        return outcome

    return fetch, finished


def test_mixed_results():
    fetch, _ = make_fetch({
        1: (0.02, "u1"),
        2: (0.01, KeyError(2)),
        3: (0.03, "u3"),
        4: (0.01, BadId("no such id")),
    })
    ok, failed = asyncio.run(fetch_report([1, 2, 3, 4], fetch))
    assert ok == {1: "u1", 3: "u3"}, (
        f"ok was {ok}. Without return_exceptions=True, gather raises on the first failure "
        "and the good results are lost."
    )
    assert failed == {2: "KeyError", 4: "BadId"}, (
        f"failed was {failed}. Store type(exc).__name__, the class NAME as a string, "
        "not the exception object or str(exc)."
    )


def test_slow_successes_survive_a_fast_failure():
    fetch, finished = make_fetch({"fast-bad": (0.01, ValueError("x")), "slow": (0.2, "done")})
    ok, failed = asyncio.run(fetch_report(["fast-bad", "slow"], fetch))
    assert ok == {"slow": "done"}, (
        f"ok was {ok}. The slow fetch must still finish after the fast one failed."
    )
    assert failed == {"fast-bad": "ValueError"}
    assert "slow" in finished, "The slow fetch did not run to its end."


def test_falsy_results_are_successes():
    fetch, _ = make_fetch({"a": (0.01, 0), "b": (0.01, None), "c": (0.01, []), "d": (0.01, "")})
    ok, failed = asyncio.run(fetch_report(["a", "b", "c", "d"], fetch))
    assert ok == {"a": 0, "b": None, "c": [], "d": ""}, (
        f"ok was {ok}. 0, None, [] and '' are real results. Test with "
        "isinstance(result, BaseException), not with 'if result:'."
    )
    assert failed == {}, f"Nothing failed, but failed was {failed}."


def test_order_follows_ids():
    fetch, _ = make_fetch({3: (0.01, "c"), 1: (0.05, "a"), 2: (0.03, "b")})
    ok, _ = asyncio.run(fetch_report([3, 1, 2], fetch))
    assert list(ok) == [3, 1, 2], f"ok's keys came out as {list(ok)}; keep the order of ids."


def test_runs_concurrently():
    plan = {i: (0.2, i) for i in range(5)}
    plan[5] = (0.2, RuntimeError("boom"))
    fetch, _ = make_fetch(plan)
    start = time.perf_counter()
    ok, failed = asyncio.run(fetch_report(list(range(6)), fetch))
    elapsed = time.perf_counter() - start
    assert len(ok) == 5 and failed == {5: "RuntimeError"}
    assert elapsed < 0.7, (
        f"6 fetches of 0.2 s took {elapsed:.2f} s; they must run concurrently (one gather call), "
        "not one by one."
    )


def test_all_fail():
    fetch, _ = make_fetch({"x": (0.01, OSError("down")), "y": (0.01, TimeoutError())})
    assert asyncio.run(fetch_report(["x", "y"], fetch)) == ({}, {"x": "OSError", "y": "TimeoutError"}), (
        "When every fetch fails, ok is empty and failed has every id."
    )


def test_empty():
    fetch, _ = make_fetch({})
    assert asyncio.run(fetch_report([], fetch)) == ({}, {}), "No ids: two empty dicts."
