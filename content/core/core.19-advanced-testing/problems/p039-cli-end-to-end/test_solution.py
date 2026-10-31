import ast
import os
import re
import subprocess
import sys
import tempfile
from functools import lru_cache
from pathlib import Path

# How this check works: your solution.py is a file of pytest tests. It is copied next to a
# file called wordstat.py that holds the code under test, and real pytest runs on it.
# First against the CORRECT code (all your tests must pass), then against several BUGGY
# copies (at least one of your tests must fail for each bug).

LEARNER = Path(__file__).with_name("solution.py")
LEARNER_SOURCE = LEARNER.read_text()

MODULE = "wordstat"
MIN_TESTS = 7
HYPOTHESIS = False

CORRECT = r'''import argparse
import json
import sys
from collections import Counter
from pathlib import Path


def build_parser():
    parser = argparse.ArgumentParser(prog="wordstat", description="Count the most common words in a text file.")
    parser.add_argument("file", help="path of a UTF-8 text file")
    parser.add_argument("--top", type=int, default=5, help="how many words to show (default 5)")
    parser.add_argument("--min-length", type=int, default=1, help="ignore shorter words (default 1)")
    parser.add_argument("--json", action="store_true", help="print a JSON object instead of lines")
    return parser


def main(argv=None):
    """Run the tool. Return the exit code: 0 success, 2 when the file cannot be read."""
    args = build_parser().parse_args(argv)
    try:
        text = Path(args.file).read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"wordstat: no such file: {args.file}", file=sys.stderr)
        return 2
    counts = Counter()
    for raw in text.lower().split():
        word = raw.strip(".,;:!?")
        if word and len(word) >= args.min_length:
            counts[word] += 1
    ranked = sorted(counts.items(), key=lambda item: (-item[1], item[0]))[: args.top]
    if args.json:
        print(json.dumps(dict(ranked)))
    else:
        for word, n in ranked:
            print(f"{word} {n}")
    return 0


if __name__ == "__main__":
    sys.exit(main())'''

# name -> (text to replace in CORRECT, replacement, what the bug does)
MUTANTS = {'top_ignored': ('[: args.top]', '', '--top is ignored, so every word is printed.'),
 'default_top_is_three': ('"--top", type=int, default=5',
                          '"--top", type=int, default=3',
                          'the default for --top is 3 instead of 5.'),
 'ties_in_first_seen_order': ('key=lambda item: (-item[1], item[0])',
                              'key=lambda item: -item[1]',
                              'words with equal counts are listed in the order they first appeared instead '
                              'of alphabetically.'),
 'case_sensitive': ('text.lower().split()',
                    'text.split()',
                    "'Apple' and 'apple' are counted as different words."),
 'punctuation_kept': ('raw.strip(".,;:!?")', 'raw', "'pear.' and 'pear' are counted as different words."),
 'min_length_off_by_one': ('len(word) >= args.min_length',
                           'len(word) > args.min_length',
                           '--min-length 2 drops words of exactly 2 letters.'),
 'json_is_a_list': ('json.dumps(dict(ranked))',
                    'json.dumps(ranked)',
                    '--json prints a list of pairs instead of an object {word: count}.'),
 'missing_file_crashes': ('    try:\n'
                          '        text = Path(args.file).read_text(encoding="utf-8")\n'
                          '    except FileNotFoundError:\n'
                          '        print(f"wordstat: no such file: {args.file}", file=sys.stderr)\n'
                          '        return 2\n',
                          '    text = Path(args.file).read_text(encoding="utf-8")\n',
                          'a missing file raises FileNotFoundError with a traceback instead of returning 2.'),
 'error_on_stdout': (', file=sys.stderr)',
                     ')',
                     'the error message goes to standard output instead of standard error.'),
 'exit_code_dropped': ('    sys.exit(main())',
                       '    main()',
                       'run as a script, the program always exits with 0 because the return value of main() '
                       'is thrown away. Only a test that starts the real program can see it.')}

# Makes hypothesis deterministic and quiet inside the temporary folder, whatever you wrote.
CONFTEST = """
from hypothesis import settings
settings.register_profile("learn", settings(derandomize=True, database=None, max_examples=100, deadline=None))
settings.load_profile("learn")
"""


def mutate(name):
    old, new, _why = MUTANTS[name]
    assert CORRECT.count(old) == 1, f"author error: snippet of {name} is not unique"
    return CORRECT.replace(old, new)


@lru_cache(maxsize=None)
def run_suite(target_source):
    with tempfile.TemporaryDirectory(prefix="learn-mut-") as tmp:
        tmp = Path(tmp)
        (tmp / (MODULE + ".py")).write_text(target_source)
        (tmp / "test_learner.py").write_text(LEARNER_SOURCE)
        (tmp / "conftest.py").write_text(CONFTEST)
        env = dict(os.environ, PYTHONPATH=str(tmp), PYTHONDONTWRITEBYTECODE="1", PYTHONUTF8="1")
        try:
            proc = subprocess.run(
                [sys.executable, "-m", "pytest", "test_learner.py", "-q", "--no-header",
                 "-p", "no:cacheprovider", "--tb=short"],
                cwd=tmp, capture_output=True, text=True, timeout=90, env=env)
        except subprocess.TimeoutExpired:
            return 124, "pytest timed out (infinite loop or a test that is far too slow?)"
    return proc.returncode, (proc.stdout + proc.stderr).replace(str(tmp), ".")


def test_tests_pass_on_the_correct_code():
    code, out = run_suite(CORRECT)
    assert code != 5, ("No tests were collected. Write functions whose names start with test_ "
                       "in solution.py.")
    assert code == 0, ("Your tests must PASS on the correct code, but they failed or crashed. "
                       "A wrong expected value or a wrong property is the usual cause. pytest said:\n"
                       + out[-1800:])


def test_you_wrote_enough_tests():
    tree = ast.parse(LEARNER_SOURCE)
    names = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name.startswith("test_")]
    assert len(names) >= MIN_TESTS, (
        f"Write at least {MIN_TESTS} test functions (names starting with test_); you have {len(names)}.")
    assert len(names) == len(set(names)), (
        "Two test functions share a name. The second silently replaces the first, so only one runs.")


def test_hypothesis_is_deterministic():
    if not HYPOTHESIS:
        return
    assert "given" in LEARNER_SOURCE, "Use hypothesis: import given and strategies, then decorate with @given(...)."
    assert "derandomize=True" in LEARNER_SOURCE and "database=None" in LEARNER_SOURCE, (
        "Put @settings(derandomize=True, database=None, max_examples=100) above every @given test. "
        "Derandomize makes the run repeatable and database=None stops hypothesis writing a .hypothesis folder.")
    for number in re.findall(r"max_examples\s*=\s*(\d+)", LEARNER_SOURCE):
        assert int(number) <= 100, "Keep max_examples at 100 or less so the checker stays fast."


def caught(name):
    _old, _new, why = MUTANTS[name]
    code, out = run_suite(mutate(name))
    assert code == 1, (
        f"Your tests did NOT catch the bug '{name}': {why} "
        "Add a test whose result differs between the correct code and the buggy one."
        + ("" if code == 0 else f" (pytest exit code {code}; output: {out[-300:]})"))

def test_catches_top_ignored():
    caught('top_ignored')

def test_catches_default_top_is_three():
    caught('default_top_is_three')

def test_catches_ties_in_first_seen_order():
    caught('ties_in_first_seen_order')

def test_catches_case_sensitive():
    caught('case_sensitive')

def test_catches_punctuation_kept():
    caught('punctuation_kept')

def test_catches_min_length_off_by_one():
    caught('min_length_off_by_one')

def test_catches_json_is_a_list():
    caught('json_is_a_list')

def test_catches_missing_file_crashes():
    caught('missing_file_crashes')

def test_catches_error_on_stdout():
    caught('error_on_stdout')

def test_catches_exit_code_dropped():
    caught('exit_code_dropped')


def test_you_use_the_right_tools():
    assert "capsys" in LEARNER_SOURCE, "Use the capsys fixture to read what main() prints."
    assert "tmp_path" in LEARNER_SOURCE, "Use tmp_path to create the input files."
    assert "subprocess" in LEARNER_SOURCE and "sys.executable" in LEARNER_SOURCE, (
        "Write one test that starts the real program: subprocess.run([sys.executable, wordstat.__file__, ...]). "
        "Always use sys.executable, never the word 'python', so the same interpreter is used.")
