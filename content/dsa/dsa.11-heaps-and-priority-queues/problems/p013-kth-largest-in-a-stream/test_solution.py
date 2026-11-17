import random
import tracemalloc

import pytest

from solution import KthLargest


class Counted:
    """A number that counts every comparison made with it (any of < <= > >=)."""
    comparisons = 0

    def __init__(self, v):
        self.v = v

    def __lt__(self, other):
        Counted.comparisons += 1
        return self.v < other.v

    def __le__(self, other):
        Counted.comparisons += 1
        return self.v <= other.v

    def __gt__(self, other):
        Counted.comparisons += 1
        return self.v > other.v

    def __ge__(self, other):
        Counted.comparisons += 1
        return self.v >= other.v


def test_the_first_example():
    s = KthLargest(3, [4, 5, 8, 2])
    got = [s.add(v) for v in (3, 5, 10, 9, 4)]
    assert got == [4, 5, 5, 8, 8], (
        f"Expected [4, 5, 5, 8, 8], got {got}. Keep the 3 largest numbers in a MIN-heap: its root (heap[0]) is the 3rd largest.")


def test_fewer_than_k_numbers_give_none():
    t = KthLargest(3, [1])
    assert t.add(2) is None, "Only two numbers (1 and 2) have been seen, so the 3rd largest does not exist: return None."
    assert t.add(3) == 1, "After 1, 2, 3 the 3rd largest is 1."
    u = KthLargest(2, [])
    assert u.add(7) is None, "An empty start: after one number there is no 2nd largest, return None."
    assert u.add(5) == 5, "After 7 and 5 the 2nd largest is 5."


def test_k_equals_one_is_the_running_maximum():
    s = KthLargest(1, [])
    got = [s.add(v) for v in (3, 1, 4, 1, 5, 9, 2, 6)]
    assert got == [3, 3, 4, 4, 5, 9, 9, 9], f"With k = 1 the answer is the maximum so far; expected [3, 3, 4, 4, 5, 9, 9, 9], got {got}."


def test_a_long_initial_list():
    s = KthLargest(2, [10, 3, 8, 1, 9, 7])
    assert s.add(2) == 9, "The two largest of 10, 3, 8, 1, 9, 7, 2 are 10 and 9: the 2nd largest is 9. Did the constructor look at ALL the initial numbers?"
    assert s.add(20) == 10, "After adding 20 the two largest are 20 and 10."


def test_duplicates_are_counted():
    s = KthLargest(2, [5, 5])
    assert s.add(5) == 5, "5, 5, 5: the 2nd largest is 5."
    assert s.add(6) == 5, "6, 5, 5, 5: the 2nd largest is 5."
    assert s.add(6) == 6, "6, 6, 5, 5, 5: the 2nd largest is 6."


def test_negative_numbers_and_floats():
    s = KthLargest(2, [-3.5, -1])
    assert s.add(-2) == -2, "-1, -2, -3.5: the 2nd largest is -2."
    assert s.add(0.5) == -1, "0.5, -1, -2, -3.5: the 2nd largest is -1."


def test_the_initial_list_is_not_changed():
    nums = [4, 5, 8, 2]
    KthLargest(3, nums)
    assert nums == [4, 5, 8, 2], "The constructor must not change the list it receives (no heapify on it, no sort)."


def test_a_small_value_does_not_push_a_big_one_out():
    s = KthLargest(2, [10, 20])
    assert s.add(1) == 10, "1 is smaller than the 2nd largest (10): it must be ignored. Do not replace the root with every new number."
    assert s.add(15) == 15, "10 leaves, 15 enters: the two largest are 20 and 15."


def test_random_streams_against_sorting():
    rng = random.Random(13)
    for _ in range(300):
        k = rng.randint(1, 8)
        start = [rng.randint(-10, 10) for _ in range(rng.randint(0, 12))]
        s = KthLargest(k, start)
        seen = list(start)
        for step in range(30):
            v = rng.randint(-10, 10)
            seen.append(v)
            want = sorted(seen, reverse=True)[k - 1] if len(seen) >= k else None
            got = s.add(v)
            assert got == want, f"k = {k}, start {start}, step {step}: after seeing {seen} the answer should be {want}, got {got}."


@pytest.mark.parametrize("order", ["random", "ascending"])
@pytest.mark.parametrize("k", [1, 5, 50])
def test_each_add_is_logarithmic(order, k):
    m = 2000
    rng = random.Random(14)
    values = rng.sample(range(10 ** 6), m + k)
    if order == "ascending":
        values.sort()
    s = KthLargest(k, [Counted(v) for v in values[:k - 1]])
    Counted.comparisons = 0
    last = None
    for v in values[k - 1:]:
        last = s.add(Counted(v))
    used = Counted.comparisons
    assert last.v == sorted(values, reverse=True)[k - 1], f"k = {k}, {order} order: the final answer is wrong."
    assert used <= 20 * m, (
        f"{m} additions with k = {k} used {used} comparisons ({used // m} per add); a heap of size k needs at most about {2 * k.bit_length() + 2} per add. "
        "Do you keep all the numbers and sort or scan them at every add?")


def test_memory_stays_small_when_the_stream_is_long():
    s = KthLargest(5, [])
    tracemalloc.start()
    before, _ = tracemalloc.get_traced_memory()
    for i in range(100_000):
        s.add((i * 7919) % 1_000_003)
    after, _ = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    assert after - before < 200_000, (
        f"After 100,000 additions with k = 5 your class holds about {after - before:,} bytes. "
        "It should keep only 5 numbers: throw away every number that cannot be among the k largest.")
