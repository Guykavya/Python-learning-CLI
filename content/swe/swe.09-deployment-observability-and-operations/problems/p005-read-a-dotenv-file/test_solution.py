import pytest

from solution import parse_dotenv


def test_simple_lines():
    assert parse_dotenv("A=1\nB=two") == {"A": "1", "B": "two"}, "Each NAME=value line gives one entry."


def test_comments_and_blank_lines():
    text = "\n# a comment\n   # an indented comment\nA=1\n\n"
    assert parse_dotenv(text) == {"A": "1"}, "Blank lines and lines starting with # (after spaces) are skipped."


def test_no_inline_comments():
    assert parse_dotenv("A=1 # note") == {"A": "1 # note"}, "There are no inline comments: the value is everything after '='."


def test_export_prefix():
    assert parse_dotenv("export APP_ENV=development") == {"APP_ENV": "development"}, "A leading 'export ' is removed."


def test_equals_inside_the_value():
    url = "postgresql://app:pw@db/app?sslmode=require&x=y"
    assert parse_dotenv(f"DATABASE_URL={url}") == {"DATABASE_URL": url}, "Split at the FIRST '=' only (str.partition)."


def test_quotes_are_removed_and_content_kept():
    text = "A=\"hello world\"\nB='cost: $5 # not a comment'\nC=\"it's\"\nD='say \"hi\"'"
    assert parse_dotenv(text) == {"A": "hello world", "B": "cost: $5 # not a comment", "C": "it's", "D": 'say "hi"'}, \
        "Matching quotes are removed; everything inside is kept as it is, including #, $ and the other kind of quote."


def test_spaces_are_trimmed():
    assert parse_dotenv("  A = 1  \n B=\"  keep  \" ") == {"A": "1", "B": "  keep  "}, \
        "Spaces around the name and around an unquoted value go; spaces inside quotes stay."


def test_no_expansion_and_no_escapes():
    assert parse_dotenv("HOME_DIR=$HOME/app\nNL=a\\nb") == {"HOME_DIR": "$HOME/app", "NL": "a\\nb"}, \
        "Do not expand $VARIABLES and do not interpret backslash sequences."


def test_empty_value_and_duplicates():
    assert parse_dotenv("A=\nB=1\nB=2") == {"A": "", "B": "2"}, "NAME= is the empty string; the last duplicate wins."


def test_windows_line_endings():
    assert parse_dotenv("A=1\r\nB=2\r\n") == {"A": "1", "B": "2"}, "A file written on Windows has \\r\\n line endings."


@pytest.mark.parametrize("text, line", [
    ("A=1\nthis is not a setting", 2),
    ("A=1\n\n=novalue", 3),
    ("1BAD=x", 1),
    ("A-B=x", 1),
    ("A=1\nGOOD=1\nB='open", 3),
    ('A="open', 1),
    ("A='mismatch\"", 1),
    ("A=\"", 1),
])
def test_errors_name_the_line(text, line):
    with pytest.raises(ValueError) as info:
        parse_dotenv(text)
    assert f"line {line}" in str(info.value), f"The error must say 'line {line}'; got {str(info.value)!r}"


def test_chapter_style_file():
    text = "APP_SECRET_KEY=abc123\nAPP_VERSION=1.0.0\n"
    assert parse_dotenv(text) == {"APP_SECRET_KEY": "abc123", "APP_VERSION": "1.0.0"}
