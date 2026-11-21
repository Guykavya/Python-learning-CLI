import itertools

import pytest

from solution import ACTIONS, STATUSES, RuleViolation, next_status

ALLOWED = {("todo", "start"): "doing", ("doing", "pause"): "todo", ("doing", "finish"): "done", ("done", "reopen"): "todo"}


@pytest.mark.parametrize("current, action", list(itertools.product(STATUSES, ACTIONS)))
def test_every_pair(current, action):
    if (current, action) in ALLOWED:
        assert next_status(current, action) == ALLOWED[(current, action)], f"{action} on a {current} task gives {ALLOWED[(current, action)]}"
    else:
        with pytest.raises(RuleViolation) as info:
            next_status(current, action)
        message = str(info.value)
        assert current in message and action in message, f"The message must name both the status ({current!r}) and the action ({action!r}); got {message!r}"


def test_the_table_has_exactly_twelve_pairs():
    assert len(list(itertools.product(STATUSES, ACTIONS))) == 12, "3 statuses x 4 actions"
    assert len(ALLOWED) == 4


def test_a_full_round_trip():
    status = "todo"
    for action in ("start", "pause", "start", "finish", "reopen"):
        status = next_status(status, action)
    assert status == "todo"


@pytest.mark.parametrize("current, action", [("blocked", "start"), ("todo", "explode"), ("", ""), ("TODO", "start"), ("todo", "Start")])
def test_unknown_words_are_a_value_error(current, action):
    with pytest.raises(ValueError):
        next_status(current, action)


def test_refused_moves_are_not_value_errors():
    with pytest.raises(RuleViolation):
        next_status("todo", "finish")
    try:
        next_status("todo", "finish")
    except ValueError:
        pytest.fail("A legal word in an illegal combination is a business refusal (RuleViolation), not a ValueError.")
    except RuleViolation:
        pass
