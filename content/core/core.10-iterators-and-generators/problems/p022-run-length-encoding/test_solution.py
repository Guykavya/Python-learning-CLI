from solution import decode, encode


def test_encode_basic():
    assert encode("WWWWBBBW") == [("W", 4), ("B", 3), ("W", 1)], "One (char, count) per run. The two W runs are separate: do not sort the text."


def test_encode_empty():
    assert encode("") == [], "Empty text gives an empty list."


def test_encode_no_repeats():
    assert encode("abc") == [("a", 1), ("b", 1), ("c", 1)], "A run of one still gets count 1."


def test_encode_alternating():
    assert encode("abab") == [("a", 1), ("b", 1), ("a", 1), ("b", 1)], "groupby only groups NEIGHBOURS. Do not count totals per letter."


def test_encode_returns_list():
    assert isinstance(encode("aab"), list), "encode returns a list of tuples."


def test_decode_basic():
    assert decode([("a", 3), ("b", 1)]) == "aaab", "Repeat each char count times and join."


def test_decode_empty():
    assert decode([]) == "", "No pairs give an empty string."


def test_round_trip():
    for text in ["hello", "aaaaaaaaaab", "  x  ", "zzz"]:
        assert decode(encode(text)) == text, f"decode(encode(t)) must give t back. It failed for {text!r}."
