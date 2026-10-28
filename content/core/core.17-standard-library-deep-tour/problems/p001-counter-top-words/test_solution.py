from collections import Counter

from solution import top_words, word_counts


def test_word_counts_is_counter():
    c = word_counts("a b a")
    assert isinstance(c, Counter), "Return a collections.Counter, not a plain dict: callers want most_common() and missing keys giving 0."
    assert c == Counter({"a": 2, "b": 1}), "Count every word: 'a b a' has 'a' twice and 'b' once."
    assert c["zzz"] == 0, "A Counter gives 0 for a missing word."


def test_word_counts_lower_case():
    c = word_counts("The THE the")
    assert c == Counter({"the": 3}), "Lower-case the text first, or 'The' and 'the' are counted as different words."


def test_word_counts_strips_punctuation():
    c = word_counts('The cat. The dog! "Hi," (she) said; ok: yes? it\'s')
    assert c["cat"] == 1 and c["dog"] == 1, "Strip punctuation from the ends: 'cat.' must count as 'cat'."
    assert c["hi"] == 1 and c["she"] == 1, "Quotes, commas and brackets at the ends are stripped too: '\"Hi,\"' becomes 'hi'."
    assert c["it's"] == 1, "Only the ENDS are stripped: the apostrophe inside \"it's\" stays."
    assert "cat." not in c, "'cat.' still has its full stop. Use word.strip(PUNCT)."


def test_word_counts_skips_empty():
    c = word_counts("wow ! !! ... wow - ok")
    assert c == Counter({"wow": 2, "-": 1, "ok": 1}), "A piece that is only punctuation ('!', '...') becomes empty after strip(): skip it. '-' is not in the strip list, so it stays."


def test_word_counts_empty_text():
    assert word_counts("") == Counter(), "Empty text has no words."
    assert word_counts("   \n\t ") == Counter(), "Only whitespace: split() gives no words."


def test_top_words_basic():
    assert top_words("b a b c a b", 2) == [("b", 3), ("a", 2)], "Most common first, as (word, count) pairs: use most_common(n)."


def test_top_words_ties_first_seen():
    assert top_words("one two three", 2) == [("one", 1), ("two", 1)], "Equal counts keep first-seen order. Do not sort ties alphabetically."
    assert top_words("zeta alpha zeta alpha mid", 3) == [("zeta", 2), ("alpha", 2), ("mid", 1)], "'zeta' appeared before 'alpha', so it comes first among the 2s."


def test_top_words_n_bounds():
    assert top_words("a b a", 10) == [("a", 2), ("b", 1)], "n larger than the number of words gives all of them, not an error."
    assert top_words("a b a", 0) == [], "n = 0 asks for nothing: []."
    assert top_words("a b a", -3) == [], "A negative n gives [] too. Careful: a hand-made slice [:n] with n = -3 drops items from the end instead."
    assert top_words("", 3) == [], "No words, nothing to return."


def test_top_words_uses_cleaning():
    assert top_words("Stop. stop! STOP? go", 1) == [("stop", 3)], "top_words should reuse word_counts so the same cleaning applies."
