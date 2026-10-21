import ast
from pathlib import Path

from solution import check_questions, interpret, is_correct, run_quiz

TREE = ast.parse(Path(__file__).with_name("solution.py").read_text())


def expect_raise(exc_type, func, *args, match=None, why=""):
    """Call func(*args). It must raise exc_type, with match in its message if match is given."""
    try:
        result = func(*args)
    except exc_type as e:
        if match is not None:
            assert match in str(e), (
                f"The {exc_type.__name__} message should contain {match!r}, but it was {str(e)!r}. {why}")
        return e
    except Exception as e:
        raise AssertionError(
            f"Expected {exc_type.__name__}, but {type(e).__name__} was raised: {e}. {why}") from e
    raise AssertionError(f"Expected {exc_type.__name__}, but the call returned {result!r}. {why}")


def script(*answers, stop_with=EOFError):
    """Fake keyboard. Returns (ask, prompts). When the answers run out, ask raises stop_with."""
    remaining = list(answers)
    prompts = []

    def ask(prompt):
        prompts.append(prompt)
        if not remaining:
            raise stop_with
        return remaining.pop(0)

    return ask, prompts


INT_Q = {"prompt": "7 x 8?", "answer": "56", "kind": "int"}
TEXT_Q = {"prompt": "Capital of Kerala?", "answer": "Thiruvananthapuram", "kind": "text"}
CHOICE_Q = {"prompt": "Which is a list?", "answer": "[1, 2]", "kind": "choice", "options": ["(1, 2)", "[1, 2]"]}


# ---------------------------------------------------------------- check_questions

def test_check_good_questions():
    assert check_questions([INT_Q, TEXT_Q, CHOICE_Q]) is None, "Valid data: return None without raising."


def test_check_empty_and_missing():
    expect_raise(ValueError, check_questions, [], match="the quiz has no questions")
    expect_raise(ValueError, check_questions, [INT_Q, {"answer": "x", "kind": "text"}],
                 match="question 2: missing 'prompt'", why="Number questions from 1.")
    expect_raise(ValueError, check_questions, [{"prompt": "p"}], match="question 1: missing 'answer'",
                 why="Check the keys in the order prompt, answer, kind.")


def test_check_kind_and_answers():
    expect_raise(ValueError, check_questions, [{"prompt": "p", "answer": "a", "kind": "essay"}],
                 match="question 1: unknown kind 'essay'; use int, text or choice")
    expect_raise(ValueError, check_questions, [{"prompt": "p", "answer": "five", "kind": "int"}],
                 match="question 1: answer 'five' is not a whole number")
    expect_raise(ValueError, check_questions, [{"prompt": "p", "answer": "a", "kind": "choice", "options": ["a"]}],
                 match="question 1: a choice question needs at least 2 options")
    expect_raise(ValueError, check_questions, [{"prompt": "p", "answer": "a", "kind": "choice"}],
                 match="needs at least 2 options", why="A choice question with no 'options' key is bad data too.")
    expect_raise(ValueError, check_questions, [{"prompt": "p", "answer": "c", "kind": "choice", "options": ["a", "b"]}],
                 match="question 1: answer 'c' is not one of the options")


# ---------------------------------------------------------------- interpret / is_correct

def test_interpret_int():
    assert interpret(INT_Q, " 56 ") == 56
    expect_raise(ValueError, interpret, INT_Q, "fifty", match="Please type a whole number, like 42.")
    expect_raise(ValueError, interpret, INT_Q, "", match="Please type a whole number")


def test_interpret_text():
    assert interpret(TEXT_Q, "  Kochi ") == "kochi", "Strip and lower-case text answers."
    expect_raise(ValueError, interpret, TEXT_Q, "   ", match="Please type an answer.")


def test_interpret_choice():
    assert interpret(CHOICE_Q, "2") == "[1, 2]", "Choice answers are option numbers from 1."
    for bad in ["0", "3", "-1", "two", ""]:
        expect_raise(ValueError, interpret, CHOICE_Q, bad, match="Please type a number from 1 to 2.",
                     why="Out-of-range numbers (including 0 and negatives) and non-numbers are both invalid.")


def test_is_correct():
    assert is_correct(INT_Q, 56) and not is_correct(INT_Q, 55)
    assert is_correct(TEXT_Q, "thiruvananthapuram"), "Compare with the answer stripped and lower-cased."
    assert is_correct(CHOICE_Q, "[1, 2]") and not is_correct(CHOICE_Q, "(1, 2)")


# ---------------------------------------------------------------- run_quiz

def test_example_run():
    ask, prompts = script("fifty-six", "56", "3", "1")
    told = []
    assert run_quiz([INT_Q, CHOICE_Q], ask=ask, tell=told.append) == 1
    assert told == ["Q1. 7 x 8?", "Please type a whole number, like 42.", "Correct!",
                    "Q2. Which is a list?", "  1) (1, 2)", "  2) [1, 2]",
                    "Please type a number from 1 to 2.", "Not quite. The answer is [1, 2].",
                    "Score: 1/2"], f"Got {told}"
    assert prompts == ["> "] * 4, "Ask with the prompt '> '."


def test_all_correct():
    ask, _ = script("56", "thiruvananthapuram", "2")
    told = []
    assert run_quiz([INT_Q, TEXT_Q, CHOICE_Q], ask=ask, tell=told.append) == 3
    assert told[-1] == "Score: 3/3"


def test_eof_stops_politely():
    ask, _ = script("56")
    told = []
    score = run_quiz([INT_Q, TEXT_Q, CHOICE_Q], ask=ask, tell=told.append)
    assert score == 1, "Return the score so far when the quiz is stopped."
    assert told[-2:] == ["Quiz stopped.", "Score: 1/3"], (
        f"Got {told[-2:]}. On EOFError: tell 'Quiz stopped.', then the score (from finally) as the last message.")


def test_ctrl_c_stops_politely():
    ask, _ = script(stop_with=KeyboardInterrupt)
    told = []
    assert run_quiz([INT_Q], ask=ask, tell=told.append) == 0
    assert told == ["Q1. 7 x 8?", "Quiz stopped.", "Score: 0/1"], f"Got {told}. Handle KeyboardInterrupt like EOFError."


def test_bad_data_stops_before_asking():
    ask, prompts = script("1")
    told = []
    expect_raise(ValueError, run_quiz, [INT_Q, {"prompt": "p", "kind": "int"}], ask, told.append,
                 match="question 2: missing 'answer'", why="Call check_questions before asking anything.")
    assert prompts == [] and told == [], "Nothing may be asked or shown when the question data is bad."


def test_score_reported_even_on_a_bug():
    def broken_ask(prompt):
        raise RuntimeError("bug in the input layer")

    told = []
    expect_raise(RuntimeError, run_quiz, [INT_Q], broken_ask, told.append,
                 why="Only EOFError and KeyboardInterrupt mean 'stop'. Other exceptions are bugs: let them propagate.")
    assert told[-1] == "Score: 0/1", "Use finally, so the score is shown on every way out."
    assert "Quiz stopped." not in told


def test_no_broad_except_and_uses_finally():
    for node in ast.walk(TREE):
        if isinstance(node, ast.ExceptHandler):
            assert node.type is not None, "No bare `except:` anywhere."
            assert ast.unparse(node.type) not in ("Exception", "BaseException"), "No `except Exception` anywhere."
    assert any(isinstance(n, ast.Try) and n.finalbody for n in ast.walk(TREE)), "Show the score in a `finally` block."
