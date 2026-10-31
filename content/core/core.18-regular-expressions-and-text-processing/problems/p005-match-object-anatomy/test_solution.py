from solution import span_info


def test_basic_digits():
    assert span_info(r"\d+", "order 66 shipped") == ("66", 6, 8), "'66' starts at index 6; end is one PAST the last digit, so 8 (like a slice)."


def test_first_match_only():
    assert span_info(r"\d+", "a1 b22 c333") == ("1", 1, 2), "re.search returns the FIRST match, not the longest one."


def test_match_at_start_and_end():
    assert span_info(r"ab", "abab") == ("ab", 0, 2), "A match at position 0 has start 0."
    assert span_info(r"z", "xyz") == ("z", 2, 3), "A match at the very end: end equals len(text)."


def test_no_match():
    assert span_info(r"cat", "dog") is None, "No match: return None, not a tuple and not an empty string."
    assert span_info(r"\d", "") is None, "Nothing to find in an empty text."


def test_empty_match_is_a_match():
    assert span_info(r"x*", "abc") == ("", 0, 0), "x* can match ZERO x's, so it matches the empty string at 0. Test 'm is None', not 'not m.group()'."
    assert span_info(r"", "") == ("", 0, 0), "The empty pattern matches the empty text."


def test_search_not_match():
    assert span_info(r"b", "abc") == ("b", 1, 2), "The match may start anywhere: use re.search, not re.match."


def test_returns_tuple():
    result = span_info(r"o", "foo")
    assert isinstance(result, tuple), "Return a tuple (text, start, end), not the Match object or a list."
    assert result == ("o", 1, 2), "The first 'o' in 'foo' is at index 1."
