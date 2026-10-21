from solution import choose


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


MENU = ["tea", "coffee", "juice"]


def bad(text):
    return f"{text!r} is not an option. Type a number from 1 to 3 or a name."


def test_by_number():
    ask, prompts = script("2")
    assert choose(MENU, ask=ask, tell=[].append) == "coffee", "Numbers count from 1: '2' is options[1]."
    assert prompts == ["Choose 1-3 or a name: "], f"Got prompts {prompts}. Use the exact prompt."


def test_by_name_ignoring_case():
    ask, _ = script("  JUICE ")
    assert choose(MENU, ask=ask, tell=[].append) == "juice", "Match names after strip(), ignoring case."


def test_example():
    ask, prompts = script("seven", "0", "Coffee")
    told = []
    result = choose(MENU, ask=ask, tell=told.append)
    assert result == "coffee", (
        f"Got {result!r}. '0' is not a valid choice: options[-1] would pick the last item. "
        "Check 1 <= number <= len(options).")
    assert told == [bad("seven"), bad("0")], (
        f"Got {told}. '0' must be rejected: options[-1] would wrongly pick the last item.")
    assert len(prompts) == 3, "Ask again after every bad answer."


def test_out_of_range_and_negative():
    ask, _ = script("4", "-1", " 3 ")
    told = []
    result = choose(MENU, ask=ask, tell=told.append)
    assert result == "juice", f"Got {result!r}. '-1' must be rejected, then ' 3 ' picks 'juice'."
    assert told == [bad("4"), bad("-1")], f"Got {told}. Only 1 to len(options) are valid numbers."


def test_message_shows_original_text():
    ask, _ = script("  ", "tea")
    told = []
    choose(MENU, ask=ask, tell=told.append)
    assert told == [bad("  ")], "Show the original answer with !r, so an empty or blank answer is visible."


def test_empty_options():
    ask, prompts = script("1")
    expect_raise(ValueError, choose, [], ask, [].append, match="options must not be empty")
    assert prompts == [], "Check for an empty list before asking."


def test_eof_propagates():
    ask, _ = script("nope")
    expect_raise(EOFError, choose, MENU, ask, [].append,
                 why="When input runs out, ask() raises EOFError: let it propagate instead of looping.")
