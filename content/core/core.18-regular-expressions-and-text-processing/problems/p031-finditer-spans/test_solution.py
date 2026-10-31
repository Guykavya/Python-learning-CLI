from solution import find_all_spans


def test_simple_numbers():
    assert find_all_spans(r"\d+", "a1 b22 c333") == [(1, 2), (4, 6), (8, 11)], "Use re.finditer and m.span() for every match. findall gives text, not positions."


def test_returns_tuples_of_ints():
    spans = find_all_spans("b", "abcb")
    assert spans == [(1, 2), (3, 4)], "Every match, left to right: 'b' is at index 1 and index 3."
    assert all(isinstance(s, tuple) for s in spans), "Each item should be a (start, end) tuple. m.span() already returns one."


def test_slicing_gives_match_back():
    text = "cat, hat and mat"
    spans = find_all_spans(r"\w+at", text)
    assert [text[s:e] for s, e in spans] == ["cat", "hat", "mat"], "end is EXCLUSIVE (like slicing): text[start:end] must be the match. Do not use end - 1."


def test_no_overlap():
    assert find_all_spans("aa", "aaaa") == [(0, 2), (2, 4)], "Matches never overlap: after (0, 2) the search continues at index 2, so (1, 3) is not a match."
    assert find_all_spans("aba", "ababa") == [(0, 3)], "After 'aba' at 0..3 only 'ba' is left, which is not a match."


def test_no_match():
    assert find_all_spans(r"\d", "no digits") == [], "No match gives an empty list, not None."
    assert find_all_spans("x", "") == [], "Empty text: nothing to find."


def test_zero_width_word_boundaries():
    assert find_all_spans(r"\b", "hi yo") == [(0, 0), (2, 2), (3, 3), (5, 5)], "\\b matches the EMPTY string at each word edge. Zero-width matches have start == end; keep them."


def test_zero_width_star():
    assert find_all_spans("a*", "baa") == [(0, 0), (1, 3), (3, 3)], "a* can match nothing: at 0 (before 'b') it matches '', at 1 it matches 'aa', and at the very end '' again. Do not filter out empty matches."
    assert find_all_spans("", "ab") == [(0, 0), (1, 1), (2, 2)], "The empty pattern matches at every position, including the end (len(text))."


def test_pattern_with_flags_inline():
    assert find_all_spans(r"(?i)ok", "OK ok Ok") == [(0, 2), (3, 5), (6, 8)], "Pass the pattern straight to re.finditer; inline flags like (?i) then just work."
