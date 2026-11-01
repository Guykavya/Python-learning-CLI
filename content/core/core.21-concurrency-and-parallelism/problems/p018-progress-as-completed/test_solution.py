import threading
import time

import pytest

from solution import run_with_progress


def job(value, seconds):
    def run():
        time.sleep(seconds)
        return value
    return run


def test_progress_follows_completion_order():
    seen = []
    funcs = [job("slow", 0.3), job("fast", 0.05), job("middle", 0.17)]
    run_with_progress(funcs, 3, lambda i, r: seen.append((i, r)))
    assert seen == [(1, "fast"), (2, "middle"), (0, "slow")], (
        f"on_done was called in this order: {seen}. It must follow FINISHING order. "
        "Loop over as_completed(futures), not over the futures list in submission order."
    )


def test_results_follow_submission_order():
    funcs = [job("slow", 0.3), job("fast", 0.05), job("middle", 0.17)]
    results = run_with_progress(funcs, 3, lambda i, r: None)
    assert results == ["slow", "fast", "middle"], (
        f"Got {results}. The RETURNED list must be in input order. Appending inside the "
        "as_completed loop gives completion order; store results[i] using the future's index."
    )


def test_jobs_overlap():
    funcs = [job(n, 0.2) for n in range(5)]
    start = time.perf_counter()
    results = run_with_progress(funcs, 5, lambda i, r: None)
    elapsed = time.perf_counter() - start
    assert results == [0, 1, 2, 3, 4], "Results must be in input order."
    assert elapsed < 0.6, (
        f"5 jobs of 0.2 s with 5 workers took {elapsed:.2f} s; one by one is 1.0 s. "
        "Submit ALL jobs before waiting for any of them."
    )


def test_on_done_runs_in_calling_thread():
    threads = []
    funcs = [job(n, 0.05) for n in range(4)]
    run_with_progress(funcs, 2, lambda i, r: threads.append(threading.current_thread()))
    assert len(threads) == 4, f"on_done must be called once per job; it was called {len(threads)} times."
    assert all(t is threading.current_thread() for t in threads), (
        "on_done was called from a worker thread. Do not use future.add_done_callback for it "
        "(callbacks run in the worker); call on_done inside your as_completed loop."
    )


def test_index_and_result_match():
    seen = {}
    funcs = [job(n * 10, 0.01 * (5 - n)) for n in range(5)]
    run_with_progress(funcs, 5, lambda i, r: seen.__setitem__(i, r))
    assert seen == {0: 0, 1: 10, 2: 20, 3: 30, 4: 40}, (
        f"on_done got {seen}. The index passed must be the job's position in funcs, "
        "not a counter of how many jobs have finished so far."
    )


def test_one_worker_means_input_order():
    seen = []
    funcs = [job("a", 0.05), job("b", 0.01), job("c", 0.03)]
    run_with_progress(funcs, 1, lambda i, r: seen.append(i))
    assert seen == [0, 1, 2], (
        f"With one worker the jobs run one after another, so they finish in input order; got {seen}. "
        "Pass max_workers=workers to the executor."
    )


def test_empty_list():
    calls = []
    assert run_with_progress([], 3, lambda i, r: calls.append(i)) == [], "No jobs means []."
    assert calls == [], "on_done must not be called when there are no jobs."


def test_error_propagates():
    def boom():
        time.sleep(0.02)
        raise ValueError("job failed")
    with pytest.raises(ValueError, match="job failed"):
        run_with_progress([job(1, 0.05), boom], 2, lambda i, r: None)
