import numpy as np

from solution import sort_records


def python_order(names, scores, ages):
    return sorted(range(len(names)), key=lambda i: (-scores[i], ages[i], names[i]))


def test_the_example():
    names = ["Eli", "Fay", "Gus", "Hal", "Ivy"]
    scores = [80, 95, 80, 80, 95]
    ages = [15, 14, 13, 15, 14]
    got = sort_records(names, scores, ages)
    assert isinstance(got, np.ndarray), f"return the order as a NumPy array, not a {type(got).__name__}."
    assert np.issubdtype(got.dtype, np.integer), f"the order is made of row positions (integers), got {got.dtype}. Return the indexes, not the sorted names."
    assert got.tolist() == [1, 4, 2, 0, 3], (
        f"expected [1, 4, 2, 0, 3], got {got.tolist()}. lexsort sorts by the LAST key first: pass (names, ages, -scores).")


def test_score_is_descending():
    got = sort_records(["a", "b", "c"], [10, 30, 20], [1, 1, 1])
    assert got.tolist() == [1, 2, 0], f"higher score first: expected [1, 2, 0], got {got.tolist()} (negate the scores for descending)."


def test_age_breaks_ties_then_name():
    got = sort_records(["Zed", "Amy", "Bob"], [50, 50, 50], [20, 20, 19])
    assert got.tolist() == [2, 1, 0], f"same score: younger first (Bob), then by name (Amy before Zed); got {got.tolist()}."


def test_full_ties_keep_original_order():
    got = sort_records(["Kim", "Kim", "Kim"], [7.5, 7.5, 7.5], [30, 30, 30])
    assert got.tolist() == [0, 1, 2], f"rows equal on every key keep their original order (lexsort is stable); got {got.tolist()}."


def test_float_scores_and_empty_input():
    got = sort_records(["x", "y"], [0.5, 0.75], [3, 3])
    assert got.tolist() == [1, 0], f"float scores: 0.75 before 0.5, got {got.tolist()}."
    empty = sort_records([], [], [])
    assert len(empty) == 0 and np.issubdtype(np.asarray(empty).dtype, np.integer), f"empty input gives an empty integer array, got {empty!r}."


def test_inputs_are_not_changed():
    names = np.array(["b", "a"])
    scores = np.array([1.0, 2.0])
    ages = np.array([5, 6])
    sort_records(names, scores, ages)
    assert names.tolist() == ["b", "a"] and scores.tolist() == [1.0, 2.0] and ages.tolist() == [5, 6], (
        "do not sort or negate the caller's arrays in place (scores *= -1 changes them).")


def test_random_tables_match_python_sorted():
    rng = np.random.default_rng(44)
    pool = np.array(["Asha", "Bilal", "Chen", "Dev", "Esha", "Farah", "Gopal"])
    for _ in range(50):
        n = int(rng.integers(1, 40))
        names = rng.choice(pool, size=n).tolist()
        scores = rng.integers(0, 6, size=n).astype(float).tolist()
        ages = rng.integers(18, 22, size=n).tolist()
        want = python_order(names, scores, ages)
        got = sort_records(names, scores, ages)
        assert got.tolist() == want, (
            f"order differs from sorted(key=(-score, age, name)).\nnames={names}\nscores={scores}\nages={ages}\n"
            f"expected {want}\ngot      {got.tolist()}")
