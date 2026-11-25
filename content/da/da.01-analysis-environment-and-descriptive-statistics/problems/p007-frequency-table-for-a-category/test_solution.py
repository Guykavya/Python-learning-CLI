import random

from solution import frequency_table


def test_example():
    got = frequency_table(["bus", "car", "bus", None, "walk", "", "bus", "car"])
    assert got == [("bus", 3, 37.5), ("(missing)", 2, 25.0), ("car", 2, 25.0), ("walk", 1, 12.5)], f"Check the missing bucket and the tie order (value ascending); got {got}"


def test_empty():
    assert frequency_table([]) == [], "No values: return an empty list (and do not divide by zero)."


def test_none_and_empty_string_share_a_bucket():
    got = frequency_table([None, "", None])
    assert got == [("(missing)", 3, 100.0)], "None and '' are both missing: one bucket '(missing)' with count 3."


def test_ties_sorted_by_value():
    got = frequency_table(["b", "a", "c", "a", "b", "c"])
    assert [r[0] for r in got] == ["a", "b", "c"], "Equal counts must be sorted by value ascending."


def test_percent_rounding():
    got = frequency_table(["x", "y", "y"])
    assert got == [("y", 2, 66.7), ("x", 1, 33.3)], "Round the percent to 1 decimal: 100 * 2 / 3 = 66.7."


def test_percent_uses_all_rows_as_the_total():
    got = frequency_table(["a", None, "a", "b"])
    assert dict((v, p) for v, c, p in got)["a"] == 50.0, "The total is the number of rows, missing ones included."


def test_random_lists_against_a_slow_count():
    for seed in range(10):
        rng = random.Random(seed)
        data = [rng.choice(["x", "y", "z", None, ""]) for _ in range(rng.randint(1, 60))]
        got = frequency_table(data)
        assert sum(c for _, c, _ in got) == len(data), "The counts must add up to the number of rows."
        assert abs(sum(p for _, _, p in got) - 100) < 0.5, "The percents should add up to about 100."
        for value, count, pct in got:
            slow = sum(1 for v in data if (v in (None, "") if value == "(missing)" else v == value))
            assert count == slow, f"Wrong count for {value!r}."
        counts = [c for _, c, _ in got]
        assert counts == sorted(counts, reverse=True), "Sort by count, largest first."
