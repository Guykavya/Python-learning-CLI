from pathlib import Path

import pytest

from solution import diff_freeze, format_diff, normalise, parse_freeze

FIX = Path(__file__).parent / "fixtures"
MONDAY = (FIX / "monday.txt").read_text(encoding="utf-8")
THURSDAY = (FIX / "thursday.txt").read_text(encoding="utf-8")
EMPTY = {"added": [], "removed": [], "upgraded": [], "downgraded": [], "changed": []}


@pytest.mark.parametrize("raw, expected", [
    ("Flask", "flask"),
    ("charset_normalizer", "charset-normalizer"),
    ("Charset.Normalizer", "charset-normalizer"),
    ("charset--normalizer", "charset-normalizer"),
    ("zope.interface", "zope-interface"),
    ("a-_.b", "a-b"),
    ("Jinja2", "jinja2"),
])
def test_normalise(raw, expected):
    assert normalise(raw) == expected, f"normalise({raw!r}) should be {expected!r}: lowercase, and a RUN of - _ . becomes ONE '-'."


def test_parse_monday():
    got = parse_freeze(MONDAY)
    assert got["flask"] == "3.0.0", "Keys are normalised names: 'Flask' -> 'flask'."
    assert got["mytool"] == "@ file:///home/kavya/mytool", "A 'name @ url' line gives the version '@ ' + url."
    assert "notes-app" not in got and len(got) == 9, "Skip comments, blank lines and lines that start with '-' (like -e). Monday has 9 packages."


def test_parse_spaces_and_blank_lines():
    got = parse_freeze("\n  requests == 2.31.0  \n\n# c\n")
    assert got == {"requests": "2.31.0"}, "Strip spaces around the name and the version, and skip blank lines."


@pytest.mark.parametrize("text, line_no", [("requests>=2.0\n", 1), ("ok==1\n\njust-a-name\n", 3), ("a==\n", 1)])
def test_parse_bad_line(text, line_no):
    with pytest.raises(ValueError) as info:
        parse_freeze(text)
    assert str(line_no) in str(info.value), "Put the line number (from 1, blank lines counted) in the error message."


def test_parse_duplicate_after_normalising():
    with pytest.raises(ValueError):
        parse_freeze("Flask==3.0.0\nflask==3.0.1\n")


def test_diff_example():
    d = diff_freeze(MONDAY, THURSDAY)
    assert d["added"] == [("markdown-it-py", "3.0.0"), ("rich", "13.7.1")], "Added: names only in the new file, sorted, with their version."
    assert d["removed"] == [("colorama", "0.4.6")], "Removed: names only in the old file."
    assert d["upgraded"] == [("certifi", "2024.2.2", "2024.7.4"), ("flask", "3.0.0", "3.0.3"), ("idna", "3.6", "3.7.0"),
                             ("jinja2", "3.1.2", "3.1.4"), ("requests", "2.31.0", "2.32.3")], "Upgraded: both versions numeric and the new one is bigger. Keep the original version strings."
    assert d["downgraded"] == [("urllib3", "2.2.0", "1.26.18")], "Downgraded: the new version is smaller. Compare as numbers part by part: (1, 26, 18) < (2, 2, 0)."
    assert d["changed"] == [("mytool", "@ file:///home/kavya/mytool", "@ file:///home/kavya/mytool-v2")], "A url cannot be compared as a number: it goes to 'changed'."


def test_name_spelling_is_not_a_change():
    d = diff_freeze("charset-normalizer==3.3.2\n", "Charset_Normalizer==3.3.2\n")
    assert d == EMPTY, "Same package, same version, only the spelling of the name differs: no change. Compare normalised names."


def test_numeric_not_string_compare():
    d = diff_freeze("pkg==3.9\n", "pkg==3.10\n")
    assert d["upgraded"] == [("pkg", "3.9", "3.10")], "3.10 is newer than 3.9. As strings '3.10' < '3.9', so compare tuples of ints."


def test_trailing_zeros_equal():
    assert diff_freeze("a==1.0\nb==2\n", "a==1.0.0\nb==2.0\n") == EMPTY, "1.0 and 1.0.0 are the same version. Remove trailing zero parts before comparing."
    d = diff_freeze("a==1.0.1\n", "a==1.1\n")
    assert d["upgraded"] == [("a", "1.0.1", "1.1")], "Only TRAILING zeros are removed: 1.0.1 < 1.1."


def test_prerelease_is_changed():
    d = diff_freeze("lib==2.0rc1\n", "lib==2.0\n")
    assert d["changed"] == [("lib", "2.0rc1", "2.0")], "A version with letters is not only numbers and dots: put it in 'changed'."


def test_same_files():
    assert diff_freeze(MONDAY, MONDAY) == EMPTY, "Identical files: every list empty."


def test_format_example():
    assert format_diff(diff_freeze(MONDAY, THURSDAY)) == [
        "+ markdown-it-py==3.0.0",
        "+ rich==13.7.1",
        "- colorama==0.4.6",
        "^ certifi 2024.2.2 -> 2024.7.4",
        "^ flask 3.0.0 -> 3.0.3",
        "^ idna 3.6 -> 3.7.0",
        "^ jinja2 3.1.2 -> 3.1.4",
        "^ requests 2.31.0 -> 2.32.3",
        "v urllib3 2.2.0 -> 1.26.18",
        "~ mytool @ file:///home/kavya/mytool -> @ file:///home/kavya/mytool-v2",
    ], "Order: added (+), removed (-), upgraded (^), downgraded (v), changed (~), each sorted by name."


def test_format_direct_reference_added():
    lines = format_diff(diff_freeze("", "tool @ file:///x\n"))
    assert lines == ["+ tool @ file:///x"], "For a direct reference, use 'name @ url', not 'name==@ url'."


def test_format_no_changes():
    assert format_diff(diff_freeze("a==1\n", "A==1.0\n")) == ["no changes"], "Nothing changed: return ['no changes']."
