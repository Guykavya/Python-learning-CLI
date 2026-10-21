from solution import convert_record


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


SCHEMA = {"name": str, "age": int, "height": float}


def test_converts_and_drops_extra_fields():
    record = {"name": "Asha", "age": "21", "height": "1.62", "city": "Pune"}
    got = convert_record(record, SCHEMA)
    assert got == {"name": "Asha", "age": 21, "height": 1.62}, f"Got {got}. Keep only schema fields, converted."
    assert record == {"name": "Asha", "age": "21", "height": "1.62", "city": "Pune"}, "Do not change the record."


def test_bad_value_message():
    expect_raise(ValueError, convert_record, {"name": "Ravi", "age": "twenty", "height": "1.7"}, SCHEMA,
                 match="field 'age': could not convert 'twenty' with int",
                 why="Name the field, show the value with !r, and the converter's __name__.")


def test_cause_is_the_original_error():
    err = expect_raise(ValueError, convert_record, {"name": "R", "age": "1", "height": "tall"}, SCHEMA)
    assert isinstance(err.__cause__, ValueError), (
        "Chain the original error: `raise ValueError(...) from e`. __cause__ was "
        f"{err.__cause__!r}.")
    assert "tall" in str(err.__cause__), "The cause should be the ValueError raised by float('tall') itself."
    assert "field 'height'" in str(err)


def test_missing_field():
    err = expect_raise(ValueError, convert_record, {"name": "Meena", "height": "1.5"}, SCHEMA,
                       match="missing field 'age'",
                       why="A missing field must be a ValueError naming it, not a raw KeyError.")
    assert err.__cause__ is None, "A missing field has no underlying cause; do not chain anything."


def test_schema_order():
    expect_raise(ValueError, convert_record, {"height": "x"}, SCHEMA, match="missing field 'name'",
                 why="Check the fields in schema order: 'name' comes first.")


def test_any_converter():
    def percent(text):
        value = int(text.rstrip("%"))
        if not 0 <= value <= 100:
            raise ValueError("percent out of range")
        return value

    assert convert_record({"p": "45%"}, {"p": percent}) == {"p": 45}
    expect_raise(ValueError, convert_record, {"p": "120%"}, {"p": percent},
                 match="field 'p': could not convert '120%' with percent")


def test_empty_schema():
    assert convert_record({"a": "1"}, {}) == {}, "No schema fields: return an empty dict."
