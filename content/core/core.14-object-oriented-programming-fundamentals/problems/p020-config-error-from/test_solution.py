import pytest

from solution import ConfigError, load_port, parse_port


def catch(func, *args):
    """Run func(*args) and return the ConfigError it raises."""
    try:
        func(*args)
    except ConfigError as e:
        return e
    except Exception as e:
        pytest.fail(f"Expected ConfigError, got {type(e).__name__}: {e}. Catch the low-level error and raise ConfigError.")
    pytest.fail("Expected ConfigError, but nothing was raised.")


def test_config_error_is_an_exception():
    assert issubclass(ConfigError, Exception), "ConfigError must inherit from Exception."


def test_valid_ports():
    assert parse_port("8080") == 8080, "parse_port('8080') returns the int 8080."
    assert parse_port(" 443 ") == 443, "Strip spaces: ' 443 ' gives 443."
    assert parse_port("1") == 1 and parse_port("65535") == 65535, "1 and 65535 are both allowed (inclusive range)."


def test_not_a_number_message():
    e = catch(parse_port, "eighty")
    assert str(e) == "port must be a number, got 'eighty'", "Message: f\"port must be a number, got {text!r}\" (note the quotes from !r)."


def test_not_a_number_is_chained_from_value_error():
    e = catch(parse_port, "eighty")
    assert isinstance(e.__cause__, ValueError), (
        "The ConfigError's __cause__ must be the original ValueError. Use: raise ConfigError(...) from e"
    )
    assert e.__suppress_context__ is True, "raise ... from e sets __suppress_context__ to True."


def test_empty_text():
    e = catch(parse_port, "   ")
    assert isinstance(e.__cause__, ValueError), "An empty port is not a number either; chain from the ValueError."


@pytest.mark.parametrize("text,number", [("0", 0), ("70000", 70000), ("-5", -5)])
def test_out_of_range(text, number):
    e = catch(parse_port, text)
    assert str(e) == f"port out of range: {number}", "Message: f\"port out of range: {number}\"."
    assert e.__cause__ is None, "An out-of-range port has no low-level cause. Do not use 'from' here."
    assert e.__context__ is None, (
        "The range error should not happen inside the except block. Do the range check after the try statement."
    )


def test_load_port_ok():
    assert load_port({"port": "8080", "host": "x"}) == 8080, "load_port reads settings['port'] and parses it."


def test_load_port_missing_key():
    e = catch(load_port, {"host": "x"})
    assert str(e) == "missing setting: port", "Message for a missing key: 'missing setting: port'."
    assert isinstance(e.__cause__, KeyError), "Chain the missing-key ConfigError from the KeyError: raise ... from e."


def test_load_port_passes_parse_errors_through():
    e = catch(load_port, {"port": "abc"})
    assert str(e) == "port must be a number, got 'abc'", "Errors from parse_port should pass through load_port unchanged."
    assert isinstance(e.__cause__, ValueError), "The pass-through error still has its ValueError cause."
    e = catch(load_port, {"port": "99999"})
    assert str(e) == "port out of range: 99999", (
        "Do not wrap parse_port's ConfigError in a new 'missing setting' error. Only the dict lookup belongs in the try."
    )
