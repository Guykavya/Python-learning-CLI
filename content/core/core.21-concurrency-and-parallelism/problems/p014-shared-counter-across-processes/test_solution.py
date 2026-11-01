import multiprocessing
import pickle

import solution
from solution import add_many, count_in_processes


def test_add_many_in_this_process():
    counter = multiprocessing.Value("i", 0)
    add_many(counter, 5)
    assert counter.value == 5, (
        f"add_many(counter, 5) should leave counter.value at 5, got {counter.value}. "
        "Take the counter as the first parameter and add to counter.value."
    )
    add_many(counter, 0)
    assert counter.value == 5, "add_many(counter, 0) must not change the value."


def test_worker_is_top_level():
    assert pickle.loads(pickle.dumps(add_many)) is add_many, (
        "add_many must be a top-level function: the child process finds it by importing "
        "solution and looking up its name."
    )


def test_four_processes_share_the_count():
    total = count_in_processes(4, 20_000)
    assert total != 0, (
        "The result is 0: each child changed its OWN copy of a variable, and the parent's copy "
        "never changed. Processes do not share memory; use multiprocessing.Value."
    )
    assert total == 80_000, (
        f"4 processes x 20,000 should give 80,000, got {total}. Lost updates: wrap "
        "'counter.value += 1' in 'with counter.get_lock():'. The GIL does not help across "
        "processes."
    )


def test_counts_are_independent_between_calls():
    assert count_in_processes(2, 50) == 100, (
        "A second call should start from 0 again: create a new Value inside count_in_processes, "
        "not at module level."
    )
