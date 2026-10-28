import inspect

import pytest

import solution
from solution import finish_order, round_robin


def test_example():
    got = round_robin([("A", 5), ("B", 2), ("C", 3)], 2)
    assert got == [("A", 2), ("B", 2), ("C", 2), ("A", 2), ("C", 1), ("A", 1)], (
        "Take from the FRONT, run min(quantum, left), and put an unfinished job at the BACK."
    )


def test_last_slice_is_short():
    assert round_robin([("X", 7)], 3) == [("X", 3), ("X", 3), ("X", 1)], (
        "The last slice runs only what is left: min(quantum, remaining), not a full quantum."
    )


def test_finished_job_does_not_return():
    got = round_robin([("A", 2), ("B", 4)], 2)
    assert got == [("A", 2), ("B", 2), ("B", 2)], "A job with 0 work left must not go back in the queue."


def test_quantum_bigger_than_all():
    got = round_robin([("A", 1), ("B", 3), ("C", 2)], 10)
    assert got == [("A", 1), ("B", 3), ("C", 2)], "A large quantum finishes each job in one slice, in arrival order."


def test_quantum_one():
    got = round_robin([("A", 3), ("B", 1), ("C", 2)], 1)
    # queue A3 B1 C2 -> A B C A C A
    assert got == [("A", 1), ("B", 1), ("C", 1), ("A", 1), ("C", 1), ("A", 1)], (
        "With quantum 1: A, B, C, then only A and C remain, then only A."
    )


def test_zero_work_skipped():
    got = round_robin([("idle", 0), ("A", 1), ("nop", 0)], 2)
    assert got == [("A", 1)], "A job with work 0 never runs and records nothing (no ('idle', 0) slice)."
    assert round_robin([], 3) == [], "No jobs: no slices."


def test_bad_quantum():
    with pytest.raises(ValueError):
        round_robin([("A", 1)], 0)
    with pytest.raises(ValueError):
        round_robin([("A", 1)], -2)


def test_input_not_changed():
    jobs = [("A", 3), ("B", 1)]
    round_robin(jobs, 2)
    assert jobs == [("A", 3), ("B", 1)], "Do not modify the caller's list: build your own deque from it."


def test_same_name_twice():
    got = round_robin([("A", 1), ("A", 2)], 1)
    assert got == [("A", 1), ("A", 1), ("A", 1)], "Jobs are separate even if two share a name."


def test_uses_deque():
    src = inspect.getsource(solution)
    assert "deque" in src, "Use collections.deque for the queue: popleft() is O(1), list.pop(0) is O(n)."
    assert "pop(0)" not in src, "list.pop(0) shifts every element; use deque.popleft()."


def test_finish_order():
    assert finish_order([("A", 5), ("B", 2), ("C", 3)], 2) == ["B", "C", "A"], "B finishes in its first slice, then C, then A."
    assert finish_order([("A", 1), ("z", 0), ("B", 1)], 5) == ["A", "B"], "Zero-work jobs never run, so they never finish."
    assert finish_order([], 1) == [], "No jobs, no finishers."


def test_long_run():
    jobs = [(f"j{i}", i % 7) for i in range(2000)]
    slices = round_robin(jobs, 3)
    assert sum(r for _, r in slices) == sum(w for _, w in jobs), "Every unit of work must be run exactly once."
    assert all(1 <= r <= 3 for _, r in slices), "Every slice runs between 1 and quantum units."
