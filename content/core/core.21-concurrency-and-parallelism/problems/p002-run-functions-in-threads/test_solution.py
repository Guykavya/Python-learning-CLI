import threading
import time

from solution import run_in_threads


def test_results_in_input_order():
    def slow_square(x, delay):
        time.sleep(delay)
        return x * x

    result = run_in_threads(slow_square, [(1, 0.15), (2, 0.05), (3, 0.1)])
    assert result == [1, 4, 9], (
        f"Got {result}. Results must follow the order of args_list, not the order the threads "
        "finished. Store each result at its index: results[i] = func(*args)."
    )


def test_each_tuple_is_unpacked():
    result = run_in_threads(lambda a, b: a + b, [(1, 2), (10, 20)])
    assert result == [3, 30], (
        f"Got {result}. Each tuple holds the positional arguments: call func(*args), not func(args)."
    )


def test_empty_list():
    assert run_in_threads(lambda x: x, []) == [], "No argument tuples: return an empty list."


def test_calls_overlap():
    def nap(x):
        time.sleep(0.2)
        return x

    start = time.perf_counter()
    result = run_in_threads(nap, [(i,) for i in range(5)])
    elapsed = time.perf_counter() - start
    assert result == [0, 1, 2, 3, 4], f"Wrong results {result}."
    assert elapsed < 0.6, (
        f"5 calls of 0.2 s took {elapsed:.2f} s; one after the other would be 1.0 s. Did you "
        "join each thread right after starting it? Start ALL threads first, then join them all."
    )


def test_all_started_before_any_finished():
    events = []
    lock = threading.Lock()

    def job(name):
        with lock:
            events.append(("start", name))
        time.sleep(0.1)
        with lock:
            events.append(("end", name))
        return name

    run_in_threads(job, [("a",), ("b",), ("c",)])
    kinds = [kind for kind, _ in events]
    assert kinds == ["start"] * 3 + ["end"] * 3, (
        f"Event order was {kinds}. All three calls should start before any of them ends. "
        "start() every thread in one loop, and join() them in a second loop."
    )


def test_really_uses_threads():
    seen = set()
    lock = threading.Lock()

    def who(_):
        with lock:
            seen.add(threading.current_thread().name)
        return None

    run_in_threads(who, [(i,) for i in range(4)])
    assert threading.main_thread().name not in seen, (
        "func ran in the main thread. Use threading.Thread(target=...) and call start(), "
        "not run() and not a plain loop."
    )
    assert len(seen) == 4, f"Expected 4 different threads, saw {len(seen)}. One Thread per tuple."


def test_threads_are_finished_on_return():
    before = threading.active_count()
    run_in_threads(time.sleep, [(0.05,), (0.1,)])
    assert threading.active_count() == before, (
        "Some threads were still running when run_in_threads returned. join() every thread "
        "before returning the results."
    )
