import threading
import time

from solution import run_until_error


class Recorder:
    def __init__(self):
        self.lock = threading.Lock()
        self.started = set()
        self.succeeded = set()
        self.running = 0

    def ok(self, i, delay):
        def func():
            with self.lock:
                self.started.add(i)
                self.running += 1
            try:
                time.sleep(delay)
            finally:
                with self.lock:
                    self.running -= 1
            with self.lock:
                self.succeeded.add(i)
            return i * 10
        return func

    def bad(self, i, delay, error):
        def func():
            with self.lock:
                self.started.add(i)
                self.running += 1
            try:
                time.sleep(delay)
            finally:
                with self.lock:
                    self.running -= 1
            raise error
        return func


def test_no_errors_returns_all_results_in_order():
    rec = Recorder()
    delays = [0.08, 0.01, 0.05, 0.02, 0.03]
    funcs = [rec.ok(i, d) for i, d in enumerate(delays)]
    results, error = run_until_error(funcs, 3)
    assert error is None, f"Nothing failed, so error must be None, got {error!r}."
    assert results == [0, 10, 20, 30, 40], (
        f"Got {results}. Return the results in INPUT order, not in the order they finished."
    )


def test_returns_the_exception_object():
    rec = Recorder()
    boom = ValueError("step 1 failed")
    funcs = [rec.ok(0, 0.01), rec.bad(1, 0.02, boom)]
    _, error = run_until_error(funcs, 2)
    assert error is boom, (
        f"Got {error!r}. Return the exception object itself (future.exception()), do not raise "
        "it and do not wrap it."
    )


def test_queued_functions_never_start_after_an_error():
    rec = Recorder()
    boom = ValueError("step 1 failed")
    funcs = [rec.ok(0, 0.05), rec.bad(1, 0.1, boom), rec.ok(2, 0.2)]
    funcs += [rec.ok(i, 0.05) for i in range(3, 23)]
    start = time.perf_counter()
    results, error = run_until_error(funcs, 2)
    elapsed = time.perf_counter() - start
    assert error is boom
    assert len(rec.started) <= 5, (
        f"{len(rec.started)} of 23 functions started. After the first error, cancel the queued "
        "futures (future.cancel() or executor.shutdown(cancel_futures=True)) so they never run."
    )
    assert {0, 1, 2} <= rec.started, "Steps 0, 1 and 2 had started before the error."
    assert elapsed < 0.8, (
        f"Took {elapsed:.2f}s; running all 23 steps takes about 0.6s. Stop at the first error."
    )


def test_results_are_the_successful_ones_in_input_order():
    rec = Recorder()
    boom = ValueError("step 1 failed")
    funcs = [rec.ok(0, 0.05), rec.bad(1, 0.1, boom), rec.ok(2, 0.2)]
    funcs += [rec.ok(i, 0.05) for i in range(3, 23)]
    results, _ = run_until_error(funcs, 2)
    expected = [i * 10 for i in sorted(rec.succeeded)]
    assert results == expected, (
        f"Got {results}, expected {expected} (the functions that finished successfully, in "
        "input order). Step 2 was already running when step 1 failed: wait for it and keep "
        "its result. Skip cancelled futures (future.cancelled()) and failed ones."
    )
    assert 2 in rec.succeeded and 20 in results, "Step 2 was running; its result belongs in results."


def test_running_functions_finish_before_return():
    rec = Recorder()
    funcs = [rec.bad(0, 0.02, KeyError("k")), rec.ok(1, 0.3)]
    run_until_error(funcs, 2)
    assert rec.running == 0, (
        f"{rec.running} function(s) were still running when you returned. Wait for the running "
        "ones: executor.shutdown(wait=True, ...) or use the executor in a 'with' block."
    )


def test_first_error_to_complete_wins():
    rec = Recorder()
    early = ValueError("fast failure")
    late = ValueError("slow failure")
    funcs = [rec.bad(0, 0.3, late), rec.bad(1, 0.02, early)]
    _, error = run_until_error(funcs, 2)
    assert error is early, (
        f"Got {error!r}. The run stops at the first failure to COMPLETE (as_completed order), "
        "which is step 1 here, not the first in the list."
    )


def test_empty_list():
    assert run_until_error([], 2) == ([], None), "No functions: ([], None)."


def test_no_threads_left_behind():
    before = threading.active_count()
    rec = Recorder()
    funcs = [rec.ok(i, 0.01) for i in range(6)] + [rec.bad(6, 0.01, RuntimeError("x"))]
    run_until_error(funcs, 3)
    time.sleep(0.05)
    assert threading.active_count() <= before, (
        f"{threading.active_count() - before} extra thread(s) are alive after return. Shut the "
        "executor down (a 'with' block or executor.shutdown())."
    )
