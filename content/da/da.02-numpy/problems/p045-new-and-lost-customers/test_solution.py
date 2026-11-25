import numpy as np

from solution import customer_changes


def test_the_example():
    jan = np.array([101, 102, 102, 103, 105])
    feb = np.array([102, 104, 105, 105, 106])
    got = customer_changes(jan, feb)
    assert isinstance(got, tuple) and len(got) == 3, f"return a tuple (new, lost, kept), got {type(got).__name__}."
    new, lost, kept = got
    assert new.tolist() == [104, 106], f"new = in February but not January: [104, 106], got {new.tolist()}. Swapped the arguments of setdiff1d?"
    assert lost.tolist() == [101, 103], f"lost = in January but not February: [101, 103], got {lost.tolist()}."
    assert kept.tolist() == [102, 105], f"kept = in both months, each id once: [102, 105], got {kept.tolist()}."
    for name, arr in (("new", new), ("lost", lost), ("kept", kept)):
        assert arr.dtype == jan.dtype, f"{name} must keep the integer dtype of the ids ({jan.dtype}), got {arr.dtype}."


def test_duplicates_are_removed_and_results_sorted():
    jan = np.array([9, 3, 3, 7, 1, 1, 1])
    feb = np.array([7, 7, 2, 9, 2, 8])
    new, lost, kept = customer_changes(jan, feb)
    assert new.tolist() == [2, 8], f"new must be sorted and without repeats: [2, 8], got {new.tolist()}."
    assert lost.tolist() == [1, 3], f"lost must be sorted and without repeats: [1, 3], got {lost.tolist()}."
    assert kept.tolist() == [7, 9], f"kept must be sorted and without repeats: [7, 9], got {kept.tolist()}. (isin keeps duplicates; use intersect1d.)"


def test_empty_months():
    empty = np.array([], dtype=np.int64)
    ids = np.array([5, 4, 5])
    new, lost, kept = customer_changes(empty, ids)
    assert new.tolist() == [4, 5] and lost.tolist() == [] and kept.tolist() == [], "January empty: everyone in February is new."
    assert new.dtype == np.int64, f"new must stay int64, got {new.dtype}."
    new, lost, kept = customer_changes(ids, empty)
    assert new.tolist() == [] and lost.tolist() == [4, 5] and kept.tolist() == [], "February empty: everyone from January is lost."
    new, lost, kept = customer_changes(empty, empty)
    assert len(new) == len(lost) == len(kept) == 0, "both months empty: three empty arrays."


def test_string_ids():
    jan = np.array(["C07", "A01", "B12"])
    feb = np.array(["B12", "D03", "A01", "A01"])
    new, lost, kept = customer_changes(jan, feb)
    assert new.tolist() == ["D03"] and lost.tolist() == ["C07"] and kept.tolist() == ["A01", "B12"], (
        f"string ids work the same way; got new={new.tolist()}, lost={lost.tolist()}, kept={kept.tolist()}.")
    assert new.dtype.kind == "U", f"string ids stay strings, got {new.dtype}."


def test_inputs_are_not_changed():
    jan = np.array([3, 1, 2])
    feb = np.array([2, 5])
    customer_changes(jan, feb)
    assert jan.tolist() == [3, 1, 2] and feb.tolist() == [2, 5], "do not sort the caller's arrays in place."


def test_random_months_match_python_sets():
    rng = np.random.default_rng(45)
    for _ in range(30):
        jan = rng.integers(0, 40, size=int(rng.integers(0, 30)))
        feb = rng.integers(0, 40, size=int(rng.integers(0, 30)))
        new, lost, kept = customer_changes(jan, feb)
        j, f = set(jan.tolist()), set(feb.tolist())
        assert new.tolist() == sorted(f - j), f"jan={jan.tolist()} feb={feb.tolist()}: new wrong."
        assert lost.tolist() == sorted(j - f), f"jan={jan.tolist()} feb={feb.tolist()}: lost wrong."
        assert kept.tolist() == sorted(j & f), f"jan={jan.tolist()} feb={feb.tolist()}: kept wrong."
