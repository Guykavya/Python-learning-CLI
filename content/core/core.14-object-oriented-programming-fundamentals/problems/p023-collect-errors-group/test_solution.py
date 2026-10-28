import pytest

from solution import validate_user

GOOD = {"name": "Kavya", "email": "k@x.in", "age": 19}


def group_for(data):
    """Call validate_user and return the ExceptionGroup it raises."""
    try:
        validate_user(data)
    except ExceptionGroup as eg:
        return eg
    except Exception as e:
        pytest.fail(
            f"Expected an ExceptionGroup, got {type(e).__name__}: {e}. "
            "Do not raise the first error; collect them all in a list and raise ExceptionGroup('invalid user', errors)."
        )
    pytest.fail(f"validate_user({data!r}) should raise an ExceptionGroup, but it returned normally.")


def summary(eg):
    return [(type(e).__name__, str(e)) for e in eg.exceptions]


def test_valid_user_returns_none():
    assert validate_user(dict(GOOD)) is None, "A valid user raises nothing and returns None."


def test_extra_keys_ignored():
    assert validate_user({**GOOD, "city": "Pune"}) is None, "Extra keys are allowed and ignored."


def test_age_limits_are_inclusive():
    assert validate_user({**GOOD, "age": 0}) is None, "Age 0 is allowed (0 to 150 inclusive)."
    assert validate_user({**GOOD, "age": 150}) is None, "Age 150 is allowed."


def test_example_three_errors():
    eg = group_for({"name": " ", "age": "19"})
    assert eg.message == "invalid user", "The group's message must be 'invalid user'."
    assert summary(eg) == [
        ("ValueError", "name must not be empty"),
        ("KeyError", "'email'"),
        ("TypeError", "age must be an int"),
    ], "Collect one error per bad field, in the order name, email, age."


def test_single_error_is_still_a_group():
    eg = group_for({**GOOD, "email": "kx.in"})
    assert summary(eg) == [("ValueError", "email must contain @")], (
        "Even one problem is raised inside an ExceptionGroup, so callers can always use except*."
    )


def test_all_missing():
    eg = group_for({})
    assert summary(eg) == [("KeyError", "'name'"), ("KeyError", "'email'"), ("KeyError", "'age'")], (
        "An empty dict misses all three keys: one KeyError(field) each, in order."
    )


@pytest.mark.parametrize("age", [-1, 151, 1000])
def test_age_out_of_range(age):
    eg = group_for({**GOOD, "age": age})
    assert summary(eg) == [("ValueError", "age must be between 0 and 150")], f"Age {age} is outside 0..150."


@pytest.mark.parametrize("age", ["19", 19.5, None])
def test_age_wrong_type(age):
    eg = group_for({**GOOD, "age": age})
    assert summary(eg) == [("TypeError", "age must be an int")], (
        f"Age {age!r} is not an int: add only the TypeError. Check the type BEFORE the range, with elif."
    )


def test_one_error_per_field():
    eg = group_for({"name": "", "email": "nope", "age": -3})
    assert len(eg.exceptions) == 3, "Each field adds at most one error. Use if/elif for the checks of one field."


def test_callers_can_use_except_star():
    caught = {}
    try:
        validate_user({"name": "", "email": "nope"})
    except* ValueError as group:
        caught["value"] = [str(e) for e in group.exceptions]
    except* KeyError as group:
        caught["key"] = [str(e) for e in group.exceptions]
    assert caught == {
        "value": ["name must not be empty", "email must contain @"],
        "key": ["'age'"],
    }, "except* ValueError should see both ValueErrors, and except* KeyError the missing age."
