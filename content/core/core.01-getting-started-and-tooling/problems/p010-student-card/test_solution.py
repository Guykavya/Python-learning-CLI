import subprocess
import sys
from pathlib import Path

SOLUTION = Path(__file__).with_name("solution.py")


def run(stdin: str = "", env=None, exe=None, cwd=None) -> list[str]:
    """Run your program with the given keyboard input and return its printed lines."""
    r = subprocess.run([exe or sys.executable, str(SOLUTION)], input=stdin,
                       capture_output=True, text=True, timeout=10, env=env, cwd=cwd)
    assert r.returncode == 0, f"Your program crashed. Read the traceback:\n{r.stderr}"
    return [line.rstrip() for line in r.stdout.strip().splitlines()]

def card(name, course, year):
    b = "+" + "-" * 20 + "+"
    return [b, "Name   : " + name, "Course : " + course, "Year   : " + year, b]


def test_example():
    assert run("Ravi Kumar\nBCA\n2\n") == card("Ravi Kumar", "BCA", "2"), (
        "Compare each line with the example in problem.md, including spaces.")


def test_other_student():
    assert run("Asha\nBSc\n3\n") == card("Asha", "BSc", "3"), (
        "Read all three values with input(); do not type them into the program.")


def test_no_prompt_text():
    out = run("A\nB\nC\n")
    assert out[0] == "+" + "-" * 20 + "+", (
        "The first printed line must be the border. If you see prompt text, use input() with no message.")


def test_labels_align():
    out = run("A\nB\nC\n")
    assert [line.index(":") for line in out[1:4]] == [7, 7, 7], (
        "The colons must line up: 'Name   :', 'Course :', 'Year   :'.")
