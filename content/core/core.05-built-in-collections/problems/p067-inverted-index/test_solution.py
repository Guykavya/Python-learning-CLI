import subprocess
import sys
from pathlib import Path

SOLUTION = Path(__file__).with_name("solution.py")


def run(stdin: str, timeout: float = 10) -> list[str]:
    """Run your program with the given keyboard input and return its printed lines."""
    try:
        r = subprocess.run([sys.executable, str(SOLUTION)], input=stdin,
                           capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise AssertionError(
            f"Your program did not finish within {timeout} seconds. Look for an infinite loop, "
            "an input() that waits for more lines than the test gives, or a slow step such as "
            "`in` on a long list inside a loop (use a set or dict instead).") from None
    assert r.returncode == 0, f"Your program crashed.\n{r.stderr}"
    return [line.rstrip() for line in r.stdout.strip().splitlines()]


def test_example():
    data = "3\nThe cat sat\nthe dog sat down\nA cat and a dog\n4\nand cat dog\nor cat down\nnot sat cat\nand fish cat\n"
    assert run(data) == ["3", "1 2 3", "2", "none"]


def test_index_not_corrupted():
    data = "2\na b\na\n2\nand a b\nor a\n"
    assert run(data) == ["1", "1 2"], (
        "After 'and a b', the set for 'a' must still be {1, 2}. If you used &= on the index's own "
        "set, you changed the index. Copy it first.")


def test_case_insensitive():
    assert run("1\nHello World\n1\nand HELLO world\n") == ["1"]


def test_unknown_words():
    assert run("1\nx\n2\nor y z\nnot x y\n") == ["none", "1"]


def test_three_words():
    assert run("3\na b c\na b\na c\n1\nand a b c\n") == ["1"]
