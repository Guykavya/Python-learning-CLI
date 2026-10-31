import re
import time

import solution

# The slow pattern is NEVER run in these tests. Expected answers were worked out by hand
# and checked against r"(\w+\s?)*" on these short strings.
CASES = [
    ("", True),
    ("hello", True),
    ("hello world", True),
    ("hello world ", True),
    ("a b c d", True),
    ("one\ttwo\nthree", True),
    ("x_1 y_2", True),
    ("hello  world", False),
    (" hello", False),
    ("hi!", False),
    ("hello world  ", False),
    ("a b c d!", False),
    (" ", False),
    ("abc def ghi ", True),
    ("a\t\tb", False),
]


def matches(s):
    return solution.SAFE_RE.fullmatch(s) is not None


def test_is_compiled_pattern():
    assert isinstance(solution.SAFE_RE, re.Pattern), "SAFE_RE must be a compiled pattern: SAFE_RE = re.compile(r'...')."


def test_accepts_same_strings():
    wrong = [(s, want) for s, want in CASES if matches(s) != want]
    assert not wrong, (
        "SAFE_RE must accept exactly what (\\w+\\s?)* accepts. Wrong answers for "
        + ", ".join(f"{s!r} (expected {'match' if want else 'no match'})" for s, want in wrong)
        + ". Words are separated by ONE whitespace character, a single trailing one is allowed, a leading one is not."
    )


def test_unicode_words_like_slow_pattern():
    assert matches("नमस्ते दुनिया") == (re.fullmatch(r"(\w+\s?)*", "नमस्ते दुनिया") is not None), "Keep using \\w and \\s like the original, so non-English words behave the same."


def time_one(s):
    start = time.perf_counter()
    solution.SAFE_RE.fullmatch(s)
    return time.perf_counter() - start


def check_near_misses():
    # Grow the input step by step and stop at the first slow one, so an exponential
    # pattern fails after about a second instead of hanging the test run.
    for n in (8, 12, 16, 20, 22, 24, 26, 28, 30):
        s = "a" * n + "!"
        took = time_one(s)
        assert took < 0.5, (
            f"SAFE_RE took {took:.2f} s on {n} letters followed by '!'. Each extra letter roughly doubles the time: "
            "the pattern still lets a run of letters be split in many ways. Make every letter matchable in only one way, "
            "e.g. require exactly one whitespace after each repeated word: (?:\\w+\\s)*\\w*."
        )


def test_fast_on_near_misses():
    check_near_misses()


def test_fast_on_long_inputs():
    check_near_misses()  # never feed long inputs to a pattern that already explodes on short ones
    for size in (500, 2000, 8000, 20000):
        for unit, tail in (("word ", "!"), ("a", "!"), ("ab ", " x")):
            s = unit * (size // len(unit)) + tail
            took = time_one(s)
            assert took < 0.5, f"SAFE_RE took {took:.2f} s on a {len(s)}-character near-miss. It should be roughly linear."
