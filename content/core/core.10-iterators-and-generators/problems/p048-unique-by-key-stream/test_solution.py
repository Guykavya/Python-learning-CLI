import itertools

from solution import new_words, unique_by


def limited(items, limit):
    for i, item in enumerate(items):
        if i >= limit:
            raise AssertionError("Too many items were read from the input: the generator is reading ahead.")
        yield item


def test_unique_plain():
    assert list(unique_by([3, 1, 3, 2, 1])) == [3, 1, 2], "Keep the first of each value, in the original order (a set alone loses the order)."


def test_unique_with_key():
    words = ["Apple", "avocado", "Bean", "beet"]
    assert list(unique_by(words, key=lambda w: w[0].lower())) == ["Apple", "Bean"], (
        "Compare by key(item) but yield the item itself, not the key."
    )


def test_unique_falsy_items():
    assert list(unique_by([0, "", None, 0, None, False])) == [0, "", None], (
        "0, '' and None are real items. Note False == 0, so False is a repeat of 0."
    )


def test_unique_infinite():
    got = list(itertools.islice(unique_by(itertools.count(), key=lambda n: n % 4), 4))
    assert got == [0, 1, 2, 3], "unique_by must work on an endless stream: no list(), no sorting."


def test_unique_no_read_ahead():
    source = limited([5, 5, 6, 7, 8], 3)
    g = unique_by(source)
    assert next(g) == 5, "First item."
    assert next(g) == 6, "The second 5 is skipped; 6 is the next new item. Do not read beyond it."


def test_unique_two_generators_independent():
    a = unique_by([1, 2])
    b = unique_by([1, 2])
    assert list(a) == [1, 2], "Both 1 and 2 are new in the first call."
    assert list(b) == [1, 2], "The seen set must be created inside the function for each call, not shared (no global, no mutable default)."


def test_new_words_example():
    lines = ["The cat sat.", "the CAT ran!", "(A) dog -- sat?"]
    assert list(new_words(lines)) == ["the", "cat", "sat", "ran", "a", "dog", "--"], (
        "Split on whitespace, strip .,!?;:\"'() from both ends, lower-case, then keep the first of each."
    )


def test_new_words_empty_pieces():
    assert list(new_words(["!! hello ... Hello?", "", "   "])) == ["hello"], (
        "Pieces that are only punctuation become empty and must be skipped. Empty lines give no words."
    )


def test_new_words_inner_punctuation_kept():
    assert list(new_words(["don't stop, don't!"])) == ["don't", "stop"], "Only strip the ends: the apostrophe inside don't stays."


def test_new_words_lazy():
    lines = limited(["one two", "two three", "boom"], 2)
    g = new_words(lines)
    assert [next(g), next(g), next(g)] == ["one", "two", "three"], (
        "new_words must be lazy: the first three new words need only the first two lines."
    )


def test_new_words_endless():
    chat = itertools.cycle(["hi there", "HI again"])
    assert list(itertools.islice(new_words(chat), 3)) == ["hi", "there", "again"], "Works on an endless stream of lines."
