from solution import ask_float


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


def script(*answers):
    """Fake keyboard. Returns (ask, prompts): ask hands out the answers, prompts records each prompt."""
    remaining = list(answers)
    prompts = []

    def ask(prompt):
        prompts.append(prompt)
        if not remaining:
            raise EOFError
        return remaining.pop(0)

    return ask, prompts


def test_first_answer_good():
    (ask, prompts), told = script("7"), []
    assert ask_float("Hours? ", 0, 10, ask=ask, tell=told.append) == 7.0, "Return the number as a float."
    assert told == [], "A good first answer needs no message."
    assert prompts == ["Hours? "], "Pass the prompt to ask() exactly once."


def test_example():
    (ask, prompts), told = script("lots", "12", "4.5"), []
    assert ask_float("Hours slept? ", 0, 10, ask=ask, tell=told.append) == 4.5
    assert told == ["'lots' is not a number. Type something like 0.",
                    "Please choose from 0 to 10, got 12.0."], f"Got messages {told}. Use the exact formats given."


def test_bounds_inclusive():
    assert ask_float("? ", 1, 5, ask=script("1")[0], tell=[].append) == 1.0, "low itself is allowed."
    assert ask_float("? ", 1, 5, ask=script("5")[0], tell=[].append) == 5.0, "high itself is allowed."


def test_nan_is_out_of_range():
    told = []
    assert ask_float("? ", 0, 10, ask=script("nan", "3")[0], tell=told.append) == 3.0
    assert told == ["Please choose from 0 to 10, got nan."], (
        f"Got {told}. float('nan') succeeds; a range check with <= is False for nan, so it is out of range.")


def test_gives_up_after_attempts():
    (ask, prompts), told = script("a", "b", "c", "5"), []
    expect_raise(ValueError, ask_float, "? ", 0, 10, ask, told.append, 3,
                 match="no valid answer after 3 attempts",
                 why="After `attempts` bad answers, raise ValueError instead of asking again.")
    assert len(prompts) == 3, f"Asked {len(prompts)} times; with attempts=3 ask exactly 3 times."
    assert len(told) == 3, "Each bad answer gets one message."


def test_attempts_validated_first():
    ask, prompts = script("5")
    expect_raise(ValueError, ask_float, "? ", 0, 10, ask, [].append, 0, match="attempts must be at least 1")
    assert prompts == [], "Check attempts BEFORE asking anything."


def test_eof_propagates():
    expect_raise(EOFError, ask_float, "? ", 0, 10, script("x")[0], [].append, 5,
                 why="When input runs out, ask() raises EOFError. Do not catch it: there is nothing to retry.")


def test_uses_ask_and_tell_not_input_print(monkeypatch):
    def forbidden(*args):
        raise AssertionError("Do not call input() or print() directly: use the ask and tell parameters.")
    monkeypatch.setattr("builtins.input", forbidden)
    monkeypatch.setattr("builtins.print", forbidden)
    assert ask_float("? ", 0, 1, ask=script("x", "1")[0], tell=[].append) == 1.0
