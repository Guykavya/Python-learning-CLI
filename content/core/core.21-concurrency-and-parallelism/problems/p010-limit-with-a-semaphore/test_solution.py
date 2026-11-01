import threading
import time

import pytest

from solution import run_limited


class Tracker:
    """Makes jobs that record how many are running at the same moment."""

    def __init__(self):
        self.running = 0
        self.peak = 0
        self.lock = threading.Lock()

    def job(self, value, delay=0.1, fail=False):
        def f():
            with self.lock:
                self.running += 1
                self.peak = max(self.peak, self.running)
            try:
                time.sleep(delay)
                if fail:
                    raise RuntimeError(f"job {value} failed")
                return value
            finally:
                with self.lock:
                    self.running -= 1
        return f


def test_peak_equals_limit():
    tr = Tracker()
    result = run_limited([tr.job(i) for i in range(8)], 3)
    assert result == list(range(8)), f"Results must be in input order, got {result}."
    assert tr.peak <= 3, (
        f"{tr.peak} jobs ran at the same time with limit 3. Every thread must take a place "
        "from ONE shared Semaphore(limit) before calling its function: with sem: ..."
    )
    assert tr.peak == 3, (
        f"Only {tr.peak} jobs ever ran together; with 8 jobs and limit 3 it should reach 3. "
        "Do not hold the semaphore while starting threads, and create it with the limit."
    )


def test_limit_one_is_one_at_a_time():
    tr = Tracker()
    result = run_limited([tr.job(c, 0.03) for c in "abcd"], 1)
    assert result == list("abcd"), f"Got {result}."
    assert tr.peak == 1, f"limit=1 must run jobs one at a time, peak was {tr.peak}."


def test_limit_bigger_than_jobs():
    tr = Tracker()
    start = time.perf_counter()
    result = run_limited([tr.job(i, 0.15) for i in range(4)], 10)
    elapsed = time.perf_counter() - start
    assert result == [0, 1, 2, 3], f"Got {result}."
    assert tr.peak == 4, f"With limit 10, all 4 jobs should run together; peak was {tr.peak}."
    assert elapsed < 0.45, f"4 jobs of 0.15 s with limit 10 took {elapsed:.2f} s; they should overlap."


@pytest.mark.filterwarnings("ignore::pytest.PytestUnhandledThreadExceptionWarning")
def test_place_is_given_back_when_a_job_raises():
    tr = Tracker()
    funcs = [tr.job("x", 0.02, fail=True), tr.job("y", 0.02), tr.job("z", 0.02)]
    done = []
    t = threading.Thread(target=lambda: done.append(run_limited(funcs, 1)), daemon=True)
    t.start()
    t.join(timeout=3)
    assert not t.is_alive(), (
        "run_limited hung after a job raised. The failing job never gave its place back: "
        "use 'with sem:' (or release() in a finally) so the place is returned on errors too."
    )
    assert done and done[0][1:] == ["y", "z"], (
        f"The jobs after the failing one must still run and return, got {done}."
    )


def test_empty():
    assert run_limited([], 3) == [], "No functions: return []."
