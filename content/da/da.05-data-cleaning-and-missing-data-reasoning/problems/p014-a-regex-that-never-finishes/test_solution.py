import subprocess
import sys
from pathlib import Path

import pytest

from solution import is_valid_ref

HERE = Path(__file__).parent

CASES = [
    ("AB-12-34-56", True),
    ("A-00-00-00", True),
    ("ABCDEF-99-99-99", True),
    ("ab-12-34-56", False),
    ("Ab-12-34-56", False),
    ("AB-1-34-56", False),
    ("AB-12-34", False),
    ("AB-12-34-567", False),
    ("AB-12-34-56 ", False),
    (" AB-12-34-56", False),
    ("AB-12-34-56\n", False),
    ("-12-34-56", False),
    ("AB-1a-34-56", False),
    ("AB12-34-56", False),
    ("AB-CD-12-34-56", False),
    ("", False),
]

NEAR_MISSES = [
    "A" * 40 + "!",
    "A" * 40 + "-12-34-5",
    "A" * 45 + "1-12-34-56",
]


def test_the_table_of_cases():
    for text, want in CASES:
        got = is_valid_ref(text)
        assert got is want, "is_valid_ref(%r) should be %s (rules in problem.md), got %r." % (text, want, got)


def test_returns_a_real_bool():
    assert is_valid_ref("AB-12-34-56") is True, "return True, not a match object."
    assert is_valid_ref("zz") is False, "return False, not None."


@pytest.mark.parametrize("text", NEAR_MISSES)
def test_near_misses_return_quickly(text):
    code = (
        "import sys; sys.path.insert(0, %r); from solution import is_valid_ref; "
        "print(is_valid_ref(sys.argv[1]))" % str(HERE)
    )
    try:
        done = subprocess.run([sys.executable, "-c", code, text], capture_output=True, text=True, timeout=2)
    except subprocess.TimeoutExpired:
        pytest.fail(
            "is_valid_ref did not finish within 2 seconds on a %d-character near miss. A quantifier inside a quantifier "
            "(like ([A-Z]+)+) makes the engine try exponentially many splits. Use one plain [A-Z]+." % len(text))
    assert done.returncode == 0, "the function crashed: %s" % done.stderr[-300:]
    assert done.stdout.strip() == "False", "a near miss is not a valid reference. Got %r." % done.stdout.strip()
