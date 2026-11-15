import threading

import pytest

from solution import Scheduler


def run_all(s, seconds=10):
    """Call s.run_all(), but fail with a message instead of hanging if it never stops."""
    box = {}

    def target():
        try:
            box["value"] = s.run_all()
        except BaseException as exc:          # pass the error on to the test
            box["error"] = exc

    t = threading.Thread(target=target, daemon=True)
    t.start()
    t.join(seconds)
    if t.is_alive():
        raise AssertionError(
            f"run_all() did not finish within {seconds} seconds. A job probably never leaves the queue: run it for "
            "min(quantum, work left), not a full quantum, so its work reaches exactly 0.")
    if "error" in box:
        raise box["error"]
    return box["value"]

# Every expected value below was traced by hand and confirmed by running the reference solution.


def test_example_from_the_statement():
    s = Scheduler(quantum=2, capacity=3)
    got = [s.submit("A", 5), s.submit("B", 3), s.submit("C", 1), s.submit("D", 2)]
    assert got == [True, True, True, False], (
        f"With capacity 3, the fourth submit must be rejected: expected [True, True, True, False], got {got}.")
    assert len(s) == 3, "Three jobs are waiting."
    order = run_all(s)
    assert order == [("C", 5), ("B", 8), ("A", 9)], (
        f"Finish order with quantum 2 should be [('C', 5), ('B', 8), ('A', 9)], got {order}. "
        "An unfinished job goes to the BACK; the clock moves by min(quantum, work left).")
    assert s.clock == 9, f"The clock ends at 9 (the total work), got {s.clock}."
    assert len(s) == 0


def test_mixed_session():
    s = Scheduler(quantum=3, capacity=2)
    assert (s.submit("A", 4), s.submit("B", 2), s.submit("C", 1)) == (True, True, False), "Capacity 2: C is rejected."
    assert s.step() == "A", "step() returns the name of the job that ran: A is at the front."
    assert s.clock == 3, f"A ran a full quantum of 3, so the clock is 3, got {s.clock}."
    assert len(s) == 2, "A has 1 unit left and went to the back: two jobs are waiting (B, A)."
    assert s.submit("C", 1) is False, "The queue is still full (B and A): C is rejected again."
    assert s.step() == "B", "B is at the front now."
    assert s.clock == 5 and s.finished == [("B", 5)], (
        f"B needed only 2 units: it finishes at 5. Got clock {s.clock}, finished {s.finished}.")
    assert s.submit("C", 1) is True, "Now only A is waiting, so C fits."
    assert s.step() == "A" and s.step() == "C", "A (1 unit left) runs, then C."
    assert s.step() is None, "step() on an empty queue returns None."
    assert s.clock == 7, f"An idle step must not move the clock: it stays at 7, got {s.clock}."
    assert s.finished == [("B", 5), ("A", 6), ("C", 7)], f"Finish order should be B@5, A@6, C@7, got {s.finished}."


def test_five_jobs_quantum_4():
    s = Scheduler(quantum=4, capacity=5)
    for name, work in [("P1", 10), ("P2", 4), ("P3", 7), ("P4", 1), ("P5", 6)]:
        assert s.submit(name, work) is True
    order = run_all(s)
    assert order == [("P2", 8), ("P4", 13), ("P3", 24), ("P5", 26), ("P1", 28)], (
        f"Expected [('P2', 8), ('P4', 13), ('P3', 24), ('P5', 26), ('P1', 28)], got {order}. "
        "Trace it: P1 runs 4 (clock 4), P2 runs 4 and finishes at 8, P3 runs 4 (12), P4 finishes at 13, "
        "P5 runs 4 (17), P1 runs 4 (21), P3 finishes at 24, P5 at 26, P1 at 28.")


def test_big_quantum_is_fifo():
    s = Scheduler(quantum=100, capacity=10)
    for name, work in [("x", 7), ("y", 1), ("z", 3)]:
        s.submit(name, work)
    assert run_all(s) == [("x", 7), ("y", 8), ("z", 11)], (
        "When the quantum is larger than every job, round robin is plain first-come, first-served.")


def test_quantum_1_interleaves():
    s = Scheduler(quantum=1, capacity=3)
    s.submit("a", 2)
    s.submit("b", 2)
    s.submit("c", 1)
    ran = [s.step() for _ in range(6)]
    assert ran == ["a", "b", "c", "a", "b", None], f"With quantum 1 the jobs take turns: a b c a b, then idle. Got {ran}."
    assert s.finished == [("c", 3), ("a", 4), ("b", 5)], f"Got {s.finished}."


def test_requeued_job_is_never_rejected():
    s = Scheduler(quantum=1, capacity=1)
    assert s.submit("solo", 3) is True
    assert s.submit("other", 1) is False, "Capacity 1: the second job is rejected."
    assert run_all(s) == [("solo", 3)], "The only job goes back to the queue twice; it must not be rejected or lost."


def test_run_all_returns_a_copy():
    s = Scheduler(2, 2)
    s.submit("a", 1)
    out = run_all(s)
    out.append(("fake", 0))
    assert s.finished == [("a", 1)], "run_all() must return a copy, so changing it does not change finished."
    assert run_all(s) == [("a", 1)], "Calling run_all() again on an empty queue changes nothing."


@pytest.mark.parametrize("args", [(0, 1), (-2, 3), (1, 0), (2, -1)])
def test_bad_construction(args):
    with pytest.raises(ValueError):
        Scheduler(*args)


@pytest.mark.parametrize("work", [0, -5])
def test_bad_work(work):
    s = Scheduler(2, 2)
    with pytest.raises(ValueError):
        s.submit("bad", work)
    assert len(s) == 0, "A rejected (invalid) job must not enter the queue."


def test_total_time_equals_total_work():
    s = Scheduler(quantum=3, capacity=50)
    works = [(i * 37) % 11 + 1 for i in range(50)]
    for i, w in enumerate(works):
        s.submit(f"j{i}", w)
    order = run_all(s)
    assert len(order) == 50, "All 50 jobs must finish."
    assert s.clock == sum(works), f"The processor is never idle while jobs wait: the clock must end at {sum(works)}."
    times = [t for _, t in order]
    assert times == sorted(times), "finished must be in the order the jobs finished (increasing times)."
