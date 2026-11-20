import random
import subprocess
import sys
from pathlib import Path

import pytest

from solution import LazyPQ

HERE = Path(__file__).parent


def size_rule(pq, where):
    assert pq.stored() >= len(pq), (
        f"{where}: stored() is {pq.stored()} but the queue holds {len(pq)} tasks: stored() counts the entries in the heap list, "
        "which must include every live task.")
    assert pq.stored() <= 4 * len(pq) + 8, (
        f"{where}: the queue holds {len(pq)} tasks but the heap list holds {pq.stored()} entries (limit 4 * {len(pq)} + 8 = "
        f"{4 * len(pq) + 8}). Rebuild the heap from the live entries when stale entries pile up, and check this after "
        "add, remove AND pop.")


def test_the_example():
    pq = LazyPQ()
    pq.add("write", 3)
    pq.add("test", 2)
    pq.add("deploy", 1)
    pq.add("write", 0)
    pq.remove("test")
    assert len(pq) == 2, f"two tasks are left (write, deploy), len() says {len(pq)}. len counts live tasks, not heap entries."
    got = [pq.pop(), pq.pop()]
    assert got == ["write", "deploy"], f"expected ['write', 'deploy'] (priority 0 and 1), got {got}."
    assert len(pq) == 0, "the queue is empty now."


def test_smaller_priority_first():
    pq = LazyPQ()
    for task, pr in (("a", 3), ("b", 2), ("c", 1), ("d", -4), ("e", 2.5)):
        pq.add(task, pr)
    got = [pq.pop() for _ in range(5)]
    assert got == ["d", "c", "b", "e", "a"], f"expected the order of priorities -4, 1, 2, 2.5, 3, got {got}."


def test_equal_priorities_leave_in_the_order_of_the_last_add():
    pq = LazyPQ()
    for task in "abc":
        pq.add(task, 5)
    pq.add("a", 5)                       # changed (same value) = added again, now the newest
    got = [pq.pop(), pq.pop(), pq.pop()]
    assert got == ["b", "c", "a"], (
        f"a task whose priority was changed counts as added at the time of the change: expected ['b', 'c', 'a'], got {got}. "
        "Take a NEW count from the counter when a task is added again.")


def test_tasks_that_cannot_be_compared():
    tasks = [object() for _ in range(6)]
    pq = LazyPQ()
    for t in tasks:
        pq.add(t, 1)
    assert [pq.pop() for _ in range(6)] == tasks, (
        "six plain objects with the same priority must come out in the order they were added. "
        "If you got a TypeError: two entries with equal priority compared the tasks. Put a unique counter between them.")


def test_remove_then_add_again():
    pq = LazyPQ()
    pq.add("x", 2)
    pq.remove("x")
    assert "x" not in pq and len(pq) == 0, "after remove the task is not in the queue."
    pq.add("x", 9)
    pq.add("y", 5)
    assert [pq.pop(), pq.pop()] == ["y", "x"], "a removed task that is added again comes with its NEW priority."


def test_contains_and_len_follow_the_live_tasks():
    pq = LazyPQ()
    pq.add("a", 1)
    pq.add("b", 2)
    assert "a" in pq and "b" in pq and "c" not in pq, "`in` asks about live tasks."
    assert pq.pop() == "a"
    assert "a" not in pq, "a popped task is no longer in the queue (delete it from your dictionary in pop)."
    pq.add("b", 0)
    assert len(pq) == 1, "changing the priority of b does not make a second b: len is 1."


def test_errors():
    pq = LazyPQ()
    with pytest.raises(KeyError):
        pq.pop()
    with pytest.raises(KeyError):
        pq.remove("nothing")
    pq.add("a", 1)
    pq.remove("a")
    with pytest.raises(KeyError):
        pq.pop()
    with pytest.raises(KeyError):
        pq.remove("a")


def test_pop_skips_stale_entries_at_the_top():
    pq = LazyPQ()
    pq.add("a", 1)
    pq.add("b", 2)
    pq.add("a", 10)                      # the entry with priority 1 is now stale and sits at the top of the heap
    assert pq.pop() == "b", "the stale entry of a (priority 1) must be skipped: b is the best live task."
    assert pq.pop() == "a"


def test_stored_counts_the_heap_list():
    pq = LazyPQ()
    assert pq.stored() == 0, "an empty queue has an empty heap list."
    pq.add("a", 1)
    pq.add("b", 2)
    assert pq.stored() >= 2, "two live tasks need at least two entries."
    assert pq.stored() <= 12, "two tasks must not need more than a few entries."


def simulate(seed, ops, tasks=6, priorities=5):
    rng = random.Random(seed)
    pq = LazyPQ()
    model = {}                           # task -> (priority, arrival number)
    arrival = 0
    for step in range(ops):
        op = rng.choice(["add", "add", "add", "remove", "pop"])
        task = rng.randrange(tasks)
        where = f"seed {seed}, step {step} ({op})"
        if op == "add":
            priority = rng.randrange(priorities)
            pq.add(task, priority)
            model[task] = (priority, arrival)
            arrival += 1
        elif op == "remove":
            if task in model:
                pq.remove(task)
                del model[task]
            else:
                with pytest.raises(KeyError):
                    pq.remove(task)
        else:
            if model:
                expected = min(model, key=lambda t: model[t])
                got = pq.pop()
                assert got == expected, (
                    f"{where}: the queue holds {dict(sorted(model.items()))} (task: (priority, arrival)); "
                    f"pop() should give {expected}, got {got}.")
                del model[expected]
            else:
                with pytest.raises(KeyError):
                    pq.pop()
        assert len(pq) == len(model), f"{where}: len is {len(pq)}, the model has {len(model)} live tasks."
        for t in range(tasks):
            assert (t in pq) == (t in model), f"{where}: `{t} in pq` should be {t in model}."
        size_rule(pq, where)


@pytest.mark.parametrize("seed", range(60))
def test_random_operations_against_a_dictionary_model(seed):
    simulate(seed, 80)


@pytest.mark.parametrize("seed", range(10))
def test_random_operations_with_many_tasks(seed):
    simulate(1000 + seed, 150, tasks=40, priorities=8)


BIG = """
import random
from solution import LazyPQ

def fail(msg):
    print("FAIL: " + msg)
    raise SystemExit

# 1. the same five tasks change 100,000 times
pq = LazyPQ()
for i in range(100000):
    pq.add(i % 5, (i * 7919) % 1000)
    if pq.stored() > 4 * len(pq) + 8:
        fail(f"after {i + 1} changes of 5 tasks the heap list holds {pq.stored()} entries (limit {4 * len(pq) + 8})")
last = {}
for i in range(100000):
    last[i % 5] = (i * 7919) % 1000
order = sorted(last, key=lambda t: (last[t], max(i for i in range(100000 - 5, 100000) if i % 5 == t)))
got = [pq.pop() for _ in range(5)]
if got != order:
    fail(f"after the changes pop() gave {got}, expected {order}")

# 2. 50,000 tasks, then all but 3 are removed
pq = LazyPQ()
for t in range(50000):
    pq.add(t, t % 97)
for t in range(3, 50000):
    pq.remove(t)
    if pq.stored() > 4 * len(pq) + 8:
        fail(f"after removing task {t} the queue has {len(pq)} tasks but the heap list holds {pq.stored()} entries")
got = [pq.pop() for _ in range(3)]
if got != [0, 1, 2]:
    fail(f"the three tasks left were 0, 1, 2 (priorities 0, 1, 2); pop gave {got}")

# 3. a long random mix against a dictionary (few tasks, so the model is cheap)
rng = random.Random(5)
pq, model, arrival = LazyPQ(), {}, 0
for step in range(100000):
    op = rng.choice(["add", "add", "remove", "pop"])
    task = rng.randrange(30)
    if op == "add":
        pr = rng.randrange(6)
        pq.add(task, pr)
        model[task] = (pr, arrival)
        arrival += 1
    elif op == "remove" and task in model:
        pq.remove(task)
        del model[task]
    elif op == "pop" and model:
        want = min(model, key=lambda t: model[t])
        got = pq.pop()
        if got != want:
            fail(f"step {step}: pop gave {got}, expected {want}")
        del model[want]
    if len(pq) != len(model) or pq.stored() > 4 * len(pq) + 8:
        fail(f"step {step}: len {len(pq)} (model {len(model)}), stored {pq.stored()}")
print("OK")
"""


def test_a_hundred_thousand_operations_in_time():
    try:
        r = subprocess.run([sys.executable, "-c", BIG], cwd=HERE, capture_output=True, text=True, timeout=10)
    except subprocess.TimeoutExpired:
        pytest.fail(
            "the big test (100,000 operations) did not finish in 10 seconds. Rebuilding the whole heap after every "
            "operation costs O(n) each time. Rebuild only when the heap list holds more than about twice the live entries.")
    assert r.returncode == 0, "your code crashed on the big test:\n" + r.stderr[-800:]
    assert r.stdout.strip() == "OK", r.stdout.strip() + "\n(the size rule is stored() <= 4 * len(pq) + 8 after every operation)"
