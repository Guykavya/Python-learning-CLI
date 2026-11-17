import ast
import random
import subprocess
import sys
from pathlib import Path

import pytest

from solution import IndexedPQ

HERE = Path(__file__).parent
SOLUTION = HERE / "solution.py"


def test_no_library_heap_and_no_sorting():
    tree = ast.parse(SOLUTION.read_text(encoding="utf-8"))
    names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
    attrs = {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
    imports = {a.name.split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
    imports |= {n.module.split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.module}
    banned = (names | attrs | imports) & {"heapq", "bisect", "insort", "sorted", "sort", "queue", "PriorityQueue",
                                          "sortedcontainers", "heapify", "heappush", "heappop", "nsmallest"}
    assert not banned, (
        f"your file uses {sorted(banned)}. This problem is about writing the heap yourself: lists, swaps, sift up, "
        "sift down and a dictionary of positions.")


def test_the_example():
    pq = IndexedPQ()
    pq.push("write", 5)
    pq.push("test", 3)
    pq.push("deploy", 8)
    assert tuple(pq.peek()) == ("test", 3), f"the smallest priority is test: 3, peek() gave {pq.peek()}."
    pq.update("deploy", 1)
    assert tuple(pq.peek()) == ("deploy", 1), "after update('deploy', 1) deploy has the best priority and must be on top."
    pq.update("test", 9)
    pq.remove("write")
    assert (len(pq), pq.stored()) == (2, 2), f"two keys are left: len and stored() must both be 2, got {(len(pq), pq.stored())}."
    got = [tuple(pq.pop_min()), tuple(pq.pop_min())]
    assert got == [("deploy", 1), ("test", 9)], f"expected [('deploy', 1), ('test', 9)], got {got}."
    assert len(pq) == 0, "the queue is empty now."


def test_pop_order_after_pushes():
    pq = IndexedPQ()
    for key, pr in zip("abcdefg", (4, 7, 1, 9, 3, 8, 2)):
        pq.push(key, pr)
    got = [tuple(pq.pop_min()) for _ in range(7)]
    assert got == [("c", 1), ("g", 2), ("e", 3), ("a", 4), ("b", 7), ("f", 8), ("d", 9)], (
        f"the keys must come out in the order of their priorities, got {got}.")


def test_update_to_a_better_priority_moves_the_key_up():
    pq = IndexedPQ()
    for key, pr in zip("abcdefg", (1, 2, 3, 4, 5, 6, 7)):
        pq.push(key, pr)
    pq.update("g", 0)
    assert tuple(pq.peek()) == ("g", 0), "g was a leaf; with priority 0 it must move up to the root. Sift UP after a smaller priority."
    assert tuple(pq.pop_min()) == ("g", 0)
    assert tuple(pq.pop_min()) == ("a", 1)


def test_update_to_a_worse_priority_moves_the_key_down():
    pq = IndexedPQ()
    for key, pr in zip("abcdefg", (1, 2, 3, 4, 5, 6, 7)):
        pq.push(key, pr)
    pq.update("a", 100)
    assert tuple(pq.peek()) == ("b", 2), (
        "a was the root; with priority 100 it must sink and b (2) must become the minimum. Sift DOWN after a bigger priority.")
    got = [pq.pop_min()[0] for _ in range(7)]
    assert got == list("bcdefga"), f"expected the order b c d e f g a, got {got}."


def test_remove_from_the_middle_may_need_a_move_up():
    # Pushed in the order 1, 4, 2, 5, 6, 7, 3 the heap is      1
    #                                                     4        2
    #                                                   5   6    7   3
    # Removing the 5 puts the last item (3) into its place, under the parent 4. Now 3 < 4: it must move UP.
    pq = IndexedPQ()
    for key, pr in (("p1", 1), ("p4", 4), ("p2", 2), ("p5", 5), ("p6", 6), ("p7", 7), ("p3", 3)):
        pq.push(key, pr)
    pq.remove("p5")
    got = [pq.pop_min()[1] for _ in range(len(pq))]
    assert got == [1, 2, 3, 4, 6, 7], (
        f"after remove('p5') the priorities must come out as [1, 2, 3, 4, 6, 7], got {got}. "
        "The item that is moved into the hole came from another branch: it can be smaller than its new parent, so it must "
        "go up; in other cases it must go down. Use the same up-or-down restore as in update.")


def test_remove_the_root_the_last_and_the_only_key():
    pq = IndexedPQ()
    for key, pr in zip("abcde", (1, 2, 3, 4, 5)):
        pq.push(key, pr)
    pq.remove("e")                                           # the last position
    pq.remove("a")                                           # the root
    assert [pq.pop_min()[0] for _ in range(len(pq))] == ["b", "c", "d"], "the root and the last key were removed."
    pq.push("z", 1)
    pq.remove("z")
    assert len(pq) == 0 and "z" not in pq, "removing the only key leaves an empty queue."


def test_priority_and_contains():
    pq = IndexedPQ()
    pq.push("a", 5)
    pq.push("b", 2)
    assert pq.priority("a") == 5 and pq.priority("b") == 2, "priority(key) is the current priority."
    pq.update("a", 1)
    assert pq.priority("a") == 1, "priority(key) shows the new priority after update."
    assert "a" in pq and "c" not in pq, "`in` asks whether the key is in the queue."
    pq.pop_min()
    assert "a" not in pq, "a popped key is no longer in the queue (delete it from your position dictionary)."
    pq.remove("b")
    assert "b" not in pq, "a removed key is no longer in the queue."


def test_errors():
    pq = IndexedPQ()
    with pytest.raises(IndexError):
        pq.pop_min()
    with pytest.raises(IndexError):
        pq.peek()
    with pytest.raises(KeyError):
        pq.update("x", 1)
    with pytest.raises(KeyError):
        pq.remove("x")
    with pytest.raises(KeyError):
        pq.priority("x")
    pq.push("x", 1)
    with pytest.raises(ValueError):
        pq.push("x", 2)
    assert pq.priority("x") == 1 and len(pq) == 1, "a refused push must not change the queue."


def test_keys_that_cannot_be_compared():
    keys = [object() for _ in range(30)]
    priorities = list(range(30))
    random.Random(2).shuffle(priorities)
    pq = IndexedPQ()
    for k, p in zip(keys, priorities):
        pq.push(k, p)
    for k, p in list(zip(keys, priorities))[:10]:
        pq.update(k, p + 100)
    expected = sorted(zip(keys, [p + 100 if i < 10 else p for i, p in enumerate(priorities)]), key=lambda kp: kp[1])
    got = [tuple(pq.pop_min()) for _ in range(30)]
    assert got == expected, "plain objects as keys: compare priorities only, never the keys."


def drain(pq):
    return [tuple(pq.pop_min()) for _ in range(len(pq))]


@pytest.mark.parametrize("n", range(2, 19))
def test_every_removal_on_small_heaps(n):
    for seed in range(10):
        rng = random.Random(n * 100 + seed)
        items = [(f"k{i}", p) for i, p in enumerate(rng.sample(range(100), n))]
        for victim in range(n):
            pq = IndexedPQ()
            for key, pr in items:
                pq.push(key, pr)
            pq.remove(items[victim][0])
            want = sorted((kp for i, kp in enumerate(items) if i != victim), key=lambda kp: kp[1])
            got = drain(pq)
            assert got == want, (
                f"pushed {items}, then remove({items[victim][0]!r}): the keys must come out as {want[:6]}..., got {got[:6]}.... "
                "After a removal from the middle the item that took its place may have to move up OR down.")


@pytest.mark.parametrize("n", range(2, 19))
def test_every_update_on_small_heaps(n):
    for seed in range(8):
        rng = random.Random(7000 + n * 100 + seed)
        items = [(f"k{i}", p) for i, p in enumerate(rng.sample(range(100), n))]
        for victim in range(n):
            for new in (-5, 500, items[rng.randrange(n)][1] + 0.5, items[rng.randrange(n)][1] - 0.5):
                pq = IndexedPQ()
                for key, pr in items:
                    pq.push(key, pr)
                pq.update(items[victim][0], new)
                changed = [(k, new if i == victim else p) for i, (k, p) in enumerate(items)]
                want = sorted(changed, key=lambda kp: kp[1])
                got = drain(pq)
                assert got == want, (
                    f"pushed {items}, then update({items[victim][0]!r}, {new}): the keys must come out as {want[:6]}..., "
                    f"got {got[:6]}.... A smaller priority moves the item up, a bigger priority moves it down.")


def simulate(seed, ops, nkeys, check_every=1):
    rng = random.Random(seed)
    pq = IndexedPQ()
    model = {}
    used = set()

    def fresh():
        while True:
            p = rng.randrange(100000) / 4
            if p not in used:
                return p

    for step in range(ops):
        op = rng.choice(["push", "push", "update", "update", "remove", "pop", "peek"])
        key = rng.randrange(nkeys)
        where = f"seed {seed}, step {step} ({op} {key})"
        if op == "push":
            if key in model:
                with pytest.raises(ValueError):
                    pq.push(key, fresh())
            else:
                p = fresh()
                pq.push(key, p)
                model[key] = p
                used.add(p)
        elif op == "update":
            if key in model:
                used.discard(model[key])
                p = fresh()
                pq.update(key, p)
                model[key] = p
                used.add(p)
            else:
                with pytest.raises(KeyError):
                    pq.update(key, 1)
        elif op == "remove":
            if key in model:
                pq.remove(key)
                used.discard(model.pop(key))
            else:
                with pytest.raises(KeyError):
                    pq.remove(key)
        elif op == "pop":
            if model:
                want = min(model.items(), key=lambda kv: kv[1])
                got = tuple(pq.pop_min())
                assert got == want, (
                    f"{where}: the queue holds {dict(sorted(model.items()))} (key: priority); pop_min() should give {want}, got {got}.")
                used.discard(model.pop(want[0]))
            else:
                with pytest.raises(IndexError):
                    pq.pop_min()
        else:
            if model:
                want = min(model.items(), key=lambda kv: kv[1])
                assert tuple(pq.peek()) == want, f"{where}: peek() should give {want}, got {pq.peek()}."
        assert len(pq) == len(model), f"{where}: len is {len(pq)}, expected {len(model)}."
        assert pq.stored() == len(model), (
            f"{where}: stored() is {pq.stored()} but the queue holds {len(model)} keys: no stale entries are allowed.")
        if step % check_every == 0:
            for k in range(nkeys):
                assert (k in pq) == (k in model), f"{where}: `{k} in pq` should be {k in model}."
                if k in model:
                    assert pq.priority(k) == model[k], f"{where}: priority({k}) should be {model[k]}, got {pq.priority(k)}."
    drained = [tuple(pq.pop_min()) for _ in range(len(model))]
    assert drained == sorted(model.items(), key=lambda kv: kv[1]), (
        f"seed {seed}: draining the queue at the end gave {drained[:6]}..., expected the keys in the order of their priorities. "
        "Some sift left the heap rule broken, or `pos` points to a wrong place.")


@pytest.mark.parametrize("seed", range(60))
def test_random_operations_small(seed):
    simulate(seed, 90, nkeys=8)


@pytest.mark.parametrize("seed", range(12))
def test_random_operations_deep_heaps(seed):
    simulate(500 + seed, 700, nkeys=150, check_every=25)


BIG = """
import random
from solution import IndexedPQ

def fail(msg):
    print("FAIL: " + msg)
    raise SystemExit

rng = random.Random(8)
n = 15000
pq = IndexedPQ()
prio = {}
for k in range(n):
    prio[k] = rng.random()
    pq.push(k, prio[k])
for _ in range(60000):
    k = rng.randrange(n)
    prio[k] = rng.random()
    pq.update(k, prio[k])
if len(pq) != n or pq.stored() != n:
    fail(f"after the updates len is {len(pq)} and stored() is {pq.stored()}, both must be {n}")
for k in rng.sample(range(n), n // 2):
    pq.remove(k)
    del prio[k]
want = sorted(prio.items(), key=lambda kv: kv[1])
got = [tuple(pq.pop_min()) for _ in range(len(prio))]
if got != want:
    fail("the keys did not come out in the order of their final priorities")
print("OK")
"""


def test_sixty_thousand_updates_in_time():
    try:
        r = subprocess.run([sys.executable, "-c", BIG], cwd=HERE, capture_output=True, text=True, timeout=10)
    except subprocess.TimeoutExpired:
        pytest.fail(
            "15,000 keys with 60,000 updates and 7,500 removals did not finish in 10 seconds. Finding a key by searching "
            "a list costs O(n). Keep a dictionary key -> position, update it in the one function that swaps, and sift "
            "from that position: O(log n) per operation.")
    assert r.returncode == 0, "your code crashed on the big test:\n" + r.stderr[-800:]
    assert r.stdout.strip() == "OK", r.stdout.strip()
