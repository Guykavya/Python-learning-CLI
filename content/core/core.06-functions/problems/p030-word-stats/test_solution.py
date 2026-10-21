from solution import word_stats
import ast
from pathlib import Path

SOURCE = Path(__file__).with_name("solution.py").read_text()
TREE = ast.parse(SOURCE)


def called_names():
    """Names of every plain function called in your code, e.g. {'print', 'len'}."""
    return {n.func.id for n in ast.walk(TREE) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}


def test_example():
    assert word_stats("The cat saw the other cat!") == {
        "words": 6, "unique": 4, "longest": "other", "average": 3.33}, (
        "6 words; 'the' and 'The' are the same word after lowercasing; '!' is stripped from 'cat!'.")


def test_punctuation_stripped():
    r = word_stats('"Hello," she said. (Really?)')
    assert r["words"] == 4 and r["longest"] == "really", (
        "Strip .,!?;:\"'() from both ends of each piece before measuring.")


def test_lone_punctuation_is_not_a_word():
    r = word_stats("wait ! ... ok")
    assert r["words"] == 2, "Pieces that are empty after stripping, like '!' and '...', are not words."
    assert r["average"] == 3.0


def test_tie_first_longest():
    assert word_stats("abc xyz")["longest"] == "abc", "On a tie, the first longest word wins."


def test_empty():
    empty = {"words": 0, "unique": 0, "longest": "", "average": 0.0}
    assert word_stats("") == empty, "No words: return the zero stats, do not divide by zero."
    assert word_stats("  !!  ?? ") == empty


def test_apostrophe_inside_kept():
    assert word_stats("don't stop")["longest"] == "don't", "strip only touches the ends of a word."


def test_has_helper_functions():
    defs = [n.name for n in TREE.body if isinstance(n, ast.FunctionDef)]
    assert len(defs) >= 3, (
        f"Only these functions are defined: {defs}. Split the work into at least two helper "
        "functions that word_stats calls.")
