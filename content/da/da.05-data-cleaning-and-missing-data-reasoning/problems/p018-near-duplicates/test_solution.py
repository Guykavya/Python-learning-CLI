import random
import time
from difflib import SequenceMatcher

from solution import similar_names

NAMES = ["John Smith", "Jon  Smith", "Joan Smythe", "Priya Nair", "Priya Nayar", "john smith"]


def slow(names, threshold):
    keys = [" ".join(n.lower().split()) for n in names]
    out = []
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            if SequenceMatcher(None, keys[i], keys[j]).ratio() >= threshold:
                out.append((i, j))
    return out


def test_the_example_default_threshold():
    got = similar_names(NAMES)
    assert got == [(0, 1), (0, 5), (1, 5), (3, 4)], (
        "expected [(0, 1), (0, 5), (1, 5), (3, 4)] (ratio 0.947, 1.0, 0.947, 0.857). Got %s." % got)


def test_threshold_is_included_and_can_be_lowered():
    got = similar_names(NAMES, threshold=0.8)
    assert (1, 2) in got, (
        "'jon smith' and 'joan smythe' have a ratio of exactly 0.8: with threshold=0.8 the pair must appear (>=, not >).")
    assert got == [(0, 1), (0, 5), (1, 2), (1, 5), (3, 4)], "got %s" % got


def test_threshold_one_means_identical_after_normalising():
    assert similar_names(NAMES, threshold=1.0) == [(0, 5)], "only 'John Smith' and 'john smith' are identical once normalised."


def test_normalising_case_and_spaces():
    got = similar_names(["ASHA   Nair", "asha nair", "\tAsha\tNair "])
    assert got == [(0, 1), (0, 2), (1, 2)], "case and runs of white space must not matter. Got %s." % got


def test_same_name_twice_is_a_pair_but_never_with_itself():
    got = similar_names(["Ravi Rao", "Ravi Rao", "Zed Quill"])
    assert got == [(0, 1)], "a name must not be paired with itself, and each pair appears once (i < j). Got %s." % got


def test_result_shape():
    got = similar_names(NAMES)
    assert isinstance(got, list) and all(isinstance(p, tuple) and len(p) == 2 and p[0] < p[1] for p in got), (
        "return a list of (i, j) tuples with i < j.")
    assert got == sorted(got), "the list must be sorted."


def test_small_lists():
    assert similar_names([]) == [] and similar_names(["only one"]) == [], "fewer than two names: no pairs."


def test_agrees_with_the_obvious_loop_on_300_names_in_time():
    rng = random.Random(5)
    first = ["asha", "ravi", "meera", "kabir", "isha", "dev", "nina", "omar", "tara", "arjun", "priya", "john"]
    last = ["nair", "smith", "rao", "khan", "patel", "iyer", "singh", "das", "mehta", "gupta"]
    names = []
    for _ in range(300):
        name = "%s %s" % (rng.choice(first), rng.choice(last))
        if rng.random() < 0.2:
            name = name.title().replace(" ", "  ")
        names.append(name)
    start = time.time()
    got = similar_names(names, threshold=0.85)
    elapsed = time.time() - start
    assert got == slow(names, 0.85), "the pairs differ from the obvious double loop on 300 names."
    assert elapsed < 15, "300 names took %.1f seconds; compare each pair once and normalise only once." % elapsed


def test_input_is_not_changed():
    names = list(NAMES)
    similar_names(names)
    assert names == NAMES
