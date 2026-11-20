import random
from collections import Counter

from solution import top_k_frequent


def model(words, k):
    counts = Counter(words)
    ordered = sorted(counts, key=lambda w: (-counts[w], w))
    return ordered[:max(k, 0)]


def test_the_chapter_examples():
    assert top_k_frequent(["i", "love", "leetcode", "i", "love", "coding"], 2) == ["i", "love"], (
        "i and love occur twice each; i comes first alphabetically.")
    got = top_k_frequent(["the", "day", "is", "sunny", "the", "the", "the", "sunny", "is", "is"], 4)
    assert got == ["the", "is", "sunny", "day"], f"Expected ['the', 'is', 'sunny', 'day'] (counts 4, 3, 2, 1), got {got}."


def test_equal_counts_are_alphabetical_not_in_order_of_appearance():
    got = top_k_frequent(["b", "a", "b", "a", "c"], 2)
    assert got == ["a", "b"], (
        f"b and a both occur twice, and a < b, so the answer is ['a', 'b']; got {got}. "
        "Counter.most_common keeps the order of first appearance for equal counts: that is not alphabetical.")
    got = top_k_frequent(["pear", "fig", "apple", "pear", "fig", "apple", "kiwi"], 3)
    assert got == ["apple", "fig", "pear"], f"Three words with count 2: alphabetical order, ['apple', 'fig', 'pear']; got {got}."


def test_the_most_frequent_not_the_least():
    got = top_k_frequent(["x", "y", "y", "z", "z", "z"], 1)
    assert got == ["z"], f"The most frequent word is z (3 times); got {got}. Is your key (-count, word) with the minus sign?"
    got = top_k_frequent(["x", "y", "y", "z", "z", "z"], 3)
    assert got == ["z", "y", "x"], f"Highest count first: ['z', 'y', 'x']; got {got}."


def test_k_zero_negative_and_too_large():
    assert top_k_frequent(["a", "b"], 0) == [], "k = 0 gives an empty list."
    assert top_k_frequent(["a", "b"], -2) == [], "A negative k gives an empty list."
    assert top_k_frequent(["b", "a", "a"], 10) == ["a", "b"], "k larger than the number of different words: return all of them in order."


def test_empty_and_single():
    assert top_k_frequent([], 3) == [], "No words: empty list."
    assert top_k_frequent(["only"], 1) == ["only"], "One word."
    assert top_k_frequent(["w"] * 5, 2) == ["w"], "One different word, repeated: the answer has just that word."


def test_case_and_exact_comparison():
    got = top_k_frequent(["b", "B", "a", "A"], 4)
    assert got == ["A", "B", "a", "b"], f"All counts are 1; Python orders capital letters first: ['A', 'B', 'a', 'b']; got {got}."
    got = top_k_frequent(["Apple", "apple", "apple"], 1)
    assert got == ["apple"], f"'Apple' and 'apple' are different words (do not lower-case): got {got}."


def test_any_iterable_and_the_input_is_not_changed():
    words = ["a", "b", "a", "c", "b", "a"]
    copy = list(words)
    assert top_k_frequent(words, 2) == ["a", "b"], "a occurs 3 times, b twice."
    assert words == copy, "Do not change the list you receive."
    assert top_k_frequent(tuple(words), 1) == ["a"], "A tuple must work."
    assert top_k_frequent((w for w in words), 2) == ["a", "b"], "A generator must work: read the words once."


def test_returns_words_not_pairs_and_a_list():
    got = top_k_frequent(["a", "a", "b"], 2)
    assert isinstance(got, list) and got == ["a", "b"], f"Return a list of words, not pairs: got {got!r}."


def test_random_inputs_against_a_full_sort():
    rng = random.Random(14)
    letters = "abcdefg"
    for _ in range(500):
        words = [rng.choice(letters) * rng.randint(1, 2) for _ in range(rng.randint(0, 40))]
        k = rng.randint(-1, 12)
        want = model(words, k)
        got = top_k_frequent(words, k)
        assert got == want, f"top_k_frequent({words}, {k}) should be {want}, got {got}."


def test_many_different_words():
    rng = random.Random(15)
    vocabulary = [f"w{i:05d}" for i in range(50_000)]
    words = [vocabulary[min(int(rng.expovariate(1 / 4000)), 49_999)] for _ in range(200_000)]
    got = top_k_frequent(words, 10)
    assert got == model(words, 10), "200,000 words with 50,000 different ones: the 10 most frequent are wrong or wrongly ordered."
