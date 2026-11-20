import pathlib
import random
import subprocess
import sys

from solution import MinuteBag

HERE = pathlib.Path(__file__).parent


def test_example():
    bag = MinuteBag(10)
    for v in (7, 3, 3, 9, 1, 3, 7):
        bag.insert(v)
    assert [bag.kth(k) for k in range(1, 8)] == [1, 3, 3, 3, 7, 7, 9]
    assert bag.kth(8) == -1 and bag.kth(0) == -1, "k outside 1..size() gives -1."
    assert (bag.remove(3), bag.remove(3), bag.remove(5)) == (True, True, False), (
        "remove returns False (and changes nothing) when there is no copy of the value.")
    assert [bag.kth(k) for k in range(1, 6)] == [1, 3, 7, 7, 9] and bag.size() == 5


def test_not_power_of_two_and_edges():
    bag = MinuteBag(5)
    for v in (4, 0, 4):
        bag.insert(v)
    assert [bag.kth(k) for k in (1, 2, 3)] == [0, 4, 4], "m = 5: the descent must stay inside 1..m."
    bag2 = MinuteBag(1)
    bag2.insert(0)
    assert bag2.kth(1) == 0 and bag2.remove(0) and bag2.kth(1) == -1


def test_random_against_sorted_list():
    rng = random.Random(1620)
    for _ in range(60):
        m = rng.randint(1, 40)
        bag, items = MinuteBag(m), []
        for step in range(40):
            if items and rng.random() < 0.35:
                v = rng.choice(items + [rng.randrange(m)])
                ok = v in items
                assert bag.remove(v) == ok, f"remove({v}) with items {sorted(items)} should be {ok}."
                if ok:
                    items.remove(v)
            else:
                v = rng.randrange(m)
                bag.insert(v)
                items.append(v)
            ordered = sorted(items)
            assert bag.size() == len(items)
            for k in range(0, len(items) + 2):
                want = ordered[k - 1] if 1 <= k <= len(items) else -1
                assert bag.kth(k) == want, f"m={m}, items={ordered}: kth({k}) should be {want}."


BIG_CODE = (
    "import random\n"
    "from solution import MinuteBag\n"
    "rng = random.Random(1620)\n"
    "m = 10**6 - 3\n"
    "bag = MinuteBag(m)\n"
    "x = 0\n"
    "for _ in range(2 * 10**5):\n"
    "    r = rng.random()\n"
    "    if r < 0.5:\n"
    "        bag.insert(rng.randrange(m))\n"
    "    elif r < 0.7:\n"
    "        bag.remove(rng.randrange(m))\n"
    "    else:\n"
    "        x ^= bag.kth(rng.randint(1, bag.size() + 1))\n"
    "print(x, bag.size(), bag.kth((bag.size() + 1) // 2))\n"
)
BIG_WANT = ['915593', '97904', '500169']


def test_large_in_time():
    try:
        r = subprocess.run([sys.executable, "-c", BIG_CODE], cwd=HERE, capture_output=True, text=True,
                           timeout=40, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, ("too slow: every operation must be O(log m). Use the binary descent for kth.")
    assert r.returncode == 0, "Your code crashed on the large input:\n" + r.stderr[-800:]
    assert r.stdout.split() == BIG_WANT, f"Large input: expected {BIG_WANT}, got {r.stdout.split()}."
