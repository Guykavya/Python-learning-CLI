import asyncio
import time

from solution import fetch_all


def make_fetch(delays):
    """A fake fetch that sleeps delays[name] and records how many run at once."""
    stats = {"running": 0, "peak": 0, "calls": []}

    async def fetch(name):
        stats["calls"].append(name)
        stats["running"] += 1
        stats["peak"] = max(stats["peak"], stats["running"])
        try:
            await asyncio.sleep(delays[name])
        finally:
            stats["running"] -= 1
        return f"data-{name}"

    return fetch, stats


def test_results_in_input_order():
    fetch, _ = make_fetch({"a": 0.15, "b": 0.01, "c": 0.08})
    result = asyncio.run(fetch_all(["a", "b", "c"], fetch))
    assert result == ["data-a", "data-b", "data-c"], (
        f"Got {result}. Results must follow the order of names, not finishing order. "
        "gather already returns them in argument order."
    )


def test_fetches_overlap():
    names = ["n1", "n2", "n3", "n4", "n5"]
    fetch, stats = make_fetch({n: 0.2 for n in names})
    start = time.perf_counter()
    asyncio.run(fetch_all(names, fetch))
    elapsed = time.perf_counter() - start
    assert stats["peak"] == 5, (
        f"At most {stats['peak']} fetch(es) were running at the same time; all 5 should be. "
        "Awaiting inside a for loop runs them one by one. Pass all coroutines to gather."
    )
    assert elapsed < 0.6, (
        f"5 fetches of 0.2 s took {elapsed:.2f} s; one by one would be 1.0 s. Run them concurrently."
    )


def test_each_name_fetched_once():
    fetch, stats = make_fetch({"x": 0.01, "y": 0.01})
    asyncio.run(fetch_all(["x", "y"], fetch))
    assert sorted(stats["calls"]) == ["x", "y"], (
        f"fetch was called with {stats['calls']}. Call it exactly once per name."
    )


def test_returns_a_list():
    fetch, _ = make_fetch({"x": 0.01})
    result = asyncio.run(fetch_all(["x"], fetch))
    assert isinstance(result, list), f"Return a list, got {type(result).__name__}."


def test_empty():
    fetch, _ = make_fetch({})
    assert asyncio.run(fetch_all([], fetch)) == [], "No names means an empty list."
