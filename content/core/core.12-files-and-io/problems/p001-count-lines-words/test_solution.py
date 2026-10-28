from solution import count_stats


def put(tmp_path, name, text):
    p = tmp_path / name
    p.write_bytes(text.encode("utf-8"))
    return p


def test_basic(tmp_path):
    p = put(tmp_path, "a.txt", "héllo wörld\nsecond line\n")
    assert count_stats(p) == (2, 4, 24), "Expected (2, 4, 24). Count characters of the decoded text, not bytes, and words with split()."


def test_str_path(tmp_path):
    p = put(tmp_path, "a.txt", "one two\n")
    assert count_stats(str(p)) == (1, 2, 8), "A str path must work too. open() accepts both str and Path."


def test_no_final_newline(tmp_path):
    p = put(tmp_path, "b.txt", "a b")
    assert count_stats(p) == (1, 2, 3), "A last line without a newline still counts as a line."


def test_empty(tmp_path):
    p = put(tmp_path, "c.txt", "")
    assert count_stats(p) == (0, 0, 0), "An empty file has 0 lines. split('\\n') would give 1, use splitlines()."


def test_messy_whitespace(tmp_path):
    p = put(tmp_path, "d.txt", "a  b\t c\n\n  d\n")
    assert count_stats(p) == (3, 4, 13), "Blank lines count as lines. Words are split on any whitespace, so use split() with no argument."


def test_chars_not_bytes(tmp_path):
    p = put(tmp_path, "e.txt", "₹₹₹")
    assert count_stats(p)[2] == 3, "'₹' is 3 bytes but 1 character. Open in text mode with encoding='utf-8'."
