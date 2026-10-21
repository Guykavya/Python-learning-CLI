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

import ast
import io
import keyword
import re
import tokenize

SNAKE = re.compile(r"^[a-z_][a-z0-9_]*$")


def source():
    return SOLUTION.read_text()


def tokens():
    return list(tokenize.generate_tokens(io.StringIO(source()).readline))


def test_same_output():
    assert run() == ["Name: Asha", "Age: 19", "Subjects: 3", "Total: 254"], (
        "Cleaning up style must not change what the program prints.")


def test_snake_case_names():
    tree = ast.parse(source())
    names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store)}
    bad = sorted(n for n in names if not SNAKE.match(n) or n in ("l", "O", "I"))
    assert not bad, f"These names break PEP 8 naming: {bad}. Use lowercase words joined by _, e.g. student_name."


def test_no_single_letter_names():
    tree = ast.parse(source())
    names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store)}
    short = sorted(n for n in names if len(n) == 1)
    assert not short, f"Give {short} a name that says what it holds, such as subject_count."


def test_no_semicolons():
    assert not [t for t in tokens() if t.type == tokenize.OP and t.string == ";"], (
        "Put each statement on its own line instead of joining them with ;")


def test_spaces_around_assignment_and_plus():
    depth = 0
    for t in tokens():
        if t.type != tokenize.OP:
            continue
        if t.string in "([{":
            depth += 1
        elif t.string in ")]}":
            depth -= 1
        elif t.string == "+" or (t.string == "=" and depth == 0):
            line = t.line
            before = line[t.start[1] - 1] if t.start[1] > 0 else " "
            after = line[t.end[1]] if t.end[1] < len(line) else " "
            assert before == " " and after == " ", (
                f"Line {t.start[0]}: put one space on each side of '{t.string}': {line.strip()}")


def test_call_and_bracket_spacing():
    toks = tokens()
    for prev, t in zip(toks, toks[1:]):
        if t.type == tokenize.OP and t.string == "(" and prev.type == tokenize.NAME \
                and not keyword.iskeyword(prev.string):
            assert prev.end == t.start, f"Line {t.start[0]}: no space between {prev.string} and '('."
    for t in toks:
        if t.type == tokenize.OP and t.string == "(":
            assert t.line[t.end[1]:t.end[1] + 1] != " ", f"Line {t.start[0]}: no space right after '('."
        if t.type == tokenize.OP and t.string == ")":
            assert t.start[1] == 0 or t.line[t.start[1] - 1] != " ", (
                f"Line {t.start[0]}: no space right before ')'.")


def test_space_after_comma():
    for t in tokens():
        if t.type == tokenize.OP and t.string == ",":
            nxt = t.line[t.end[1]:t.end[1] + 1]
            assert nxt in (" ", "\n", "", ")"), f"Line {t.start[0]}: put a space after the comma."


def test_line_length():
    long = [i for i, line in enumerate(source().splitlines(), 1) if len(line) > 79]
    assert not long, f"Lines longer than 79 characters: {long}"
