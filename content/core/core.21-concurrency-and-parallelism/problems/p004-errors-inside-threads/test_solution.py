import threading
import time

from solution import run_and_collect


def test_successes_only():
    result = run_and_collect([lambda: 1, lambda: "two", lambda: None])
    assert result == [("ok", 1), ("ok", "two"), ("ok", None)], (
        f"Got {result}. Each success is the tuple ('ok', value), even when the value is None."
    )


def test_error_is_the_exception_object():
    err = ValueError("no data")

    def bad():
        raise err

    result = run_and_collect([lambda: 42, bad])
    assert result[0] == ("ok", 42), f"First entry should be ('ok', 42), got {result[0]}."
    assert result[1] is not None, (
        "The failing function's slot is None: the exception killed the thread before it stored "
        "anything. Wrap the call in try/except inside the thread."
    )
    status, value = result[1]
    assert status == "error", f"A raising function must give 'error', got {status!r}."
    assert value is err, (
        f"Store the exception OBJECT itself, got {value!r}. Not str(exc), not type(exc)."
    )


def test_order_follows_input_not_finish_time():
    def slow_fail():
        time.sleep(0.15)
        raise KeyError("late")

    def fast():
        time.sleep(0.01)
        return "fast"

    result = run_and_collect([slow_fail, fast])
    assert [s for s, _ in result] == ["error", "ok"], (
        f"Statuses were {[s for s, _ in result]}. Keep input order: store by index, do not append."
    )
    assert isinstance(result[0][1], KeyError), "The first entry should hold the KeyError."


def test_one_error_does_not_stop_the_others():
    ran = []
    lock = threading.Lock()

    def make(i):
        def f():
            with lock:
                ran.append(i)
            if i % 2:
                raise RuntimeError(f"job {i}")
            return i
        return f

    result = run_and_collect([make(i) for i in range(6)])
    assert sorted(ran) == list(range(6)), f"Only jobs {sorted(ran)} ran. Every function must run."
    assert [s for s, _ in result] == ["ok", "error"] * 3, f"Wrong statuses: {result}."
    assert str(result[3][1]) == "job 3", "Each error entry must hold that job's own exception."


def test_runs_concurrently():
    def nap():
        time.sleep(0.2)
        return "done"

    def nap_fail():
        time.sleep(0.2)
        raise OSError("disk")

    start = time.perf_counter()
    result = run_and_collect([nap, nap_fail, nap, nap_fail, nap])
    elapsed = time.perf_counter() - start
    assert len(result) == 5, f"Expected 5 entries, got {len(result)}."
    assert elapsed < 0.6, (
        f"5 calls of 0.2 s took {elapsed:.2f} s. Start all threads before joining any."
    )


def test_empty():
    assert run_and_collect([]) == [], "No functions: return []."
