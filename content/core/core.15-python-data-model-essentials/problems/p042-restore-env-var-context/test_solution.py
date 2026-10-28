import os

import pytest

from solution import temp_env

NAME = "LEARN_TEST_VAR"
OTHER = "LEARN_TEST_OTHER"


@pytest.fixture(autouse=True)
def clean_env():
    saved = {k: os.environ.get(k) for k in (NAME, OTHER)}
    for k in saved:
        os.environ.pop(k, None)
    yield
    for k, v in saved.items():
        if v is None:
            os.environ.pop(k, None)
        else:
            os.environ[k] = v


def test_sets_variable_inside_and_removes_after_if_it_did_not_exist():
    with temp_env(LEARN_TEST_VAR="on"):
        assert os.environ.get(NAME) == "on", "Inside the block the variable must be set."
    assert NAME not in os.environ, "A variable that did not exist before must be DELETED again afterwards (not set to None or '')."


def test_restores_previous_value():
    os.environ[NAME] = "old"
    with temp_env(LEARN_TEST_VAR="new"):
        assert os.environ[NAME] == "new", "Inside the block the new value is visible."
    assert os.environ[NAME] == "old", "Afterwards the OLD value must come back: save it before changing."


def test_value_none_removes_variable_temporarily():
    os.environ[NAME] = "here"
    with temp_env(LEARN_TEST_VAR=None):
        assert NAME not in os.environ, "A value of None means: remove the variable inside the block."
    assert os.environ[NAME] == "here", "...and put it back afterwards."


def test_restores_even_when_block_raises():
    os.environ[NAME] = "old"
    with pytest.raises(RuntimeError):
        with temp_env(LEARN_TEST_VAR="new"):
            raise RuntimeError("boom")
    assert os.environ[NAME] == "old", "Restore in a `finally` so the old value comes back when the block raises (and the exception must still propagate)."


def test_several_variables_and_non_string_values():
    os.environ[OTHER] = "keep"
    with temp_env(LEARN_TEST_VAR=5, LEARN_TEST_OTHER="x") as env:
        assert os.environ[NAME] == "5", "Non-string values are converted with str(): os.environ only accepts strings."
        assert os.environ[OTHER] == "x", "All variables are changed."
        assert env is os.environ, "The manager yields os.environ."
    assert NAME not in os.environ and os.environ[OTHER] == "keep", "All variables are restored independently."


def test_unrelated_variables_untouched():
    before = dict(os.environ)
    with temp_env(LEARN_TEST_VAR="1"):
        pass
    assert dict(os.environ) == before, "The environment must be exactly as before after the block."


def test_nested_use():
    with temp_env(LEARN_TEST_VAR="outer"):
        with temp_env(LEARN_TEST_VAR="inner"):
            assert os.environ[NAME] == "inner", "Inner value wins inside."
        assert os.environ[NAME] == "outer", "After the inner block the OUTER value is restored (not removed)."
    assert NAME not in os.environ, "After the outer block it is gone."


def test_setup_failure_still_restores():
    os.environ[NAME] = "old"
    with pytest.raises((ValueError, TypeError)):
        with temp_env(LEARN_TEST_VAR="new", LEARN_TEST_OTHER="bad\x00value"):
            pass
    assert os.environ[NAME] == "old", "If setting a later variable fails, the earlier changes must still be undone: put the changes inside the `try` too."
    assert OTHER not in os.environ, "No half-applied changes may remain."
