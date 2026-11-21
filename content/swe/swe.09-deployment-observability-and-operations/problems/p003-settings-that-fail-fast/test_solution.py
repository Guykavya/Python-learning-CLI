import dataclasses

import pytest

from solution import ConfigError, Settings

GOOD = {"DATABASE_URL": "sqlite:///dev.db", "SECRET_KEY": "k" * 32}


def test_defaults():
    s = Settings.from_env(GOOD)
    assert (s.database_url, s.secret_key, s.port, s.log_level) == ("sqlite:///dev.db", "k" * 32, 8000, "INFO"), \
        f"Defaults: port 8000, log level INFO; got {s}"


def test_values_are_converted():
    s = Settings.from_env({**GOOD, "PORT": "9090", "LOG_LEVEL": "debug"})
    assert s.port == 9090 and isinstance(s.port, int), "PORT must be converted to an int."
    assert s.log_level == "DEBUG", "LOG_LEVEL is case-insensitive and stored in upper case."


def test_is_frozen():
    s = Settings.from_env(GOOD)
    with pytest.raises(dataclasses.FrozenInstanceError):
        s.port = 1


def test_missing_required():
    with pytest.raises(ConfigError) as info:
        Settings.from_env({})
    text = str(info.value)
    assert "DATABASE_URL" in text and "SECRET_KEY" in text, \
        f"Both missing variables must be named in ONE error, so the person fixing the deploy sees everything; got {text!r}"


def test_empty_string_is_not_set():
    with pytest.raises(ConfigError, match="DATABASE_URL"):
        Settings.from_env({"DATABASE_URL": "", "SECRET_KEY": "k" * 32})


def test_every_problem_in_one_error():
    with pytest.raises(ConfigError) as info:
        Settings.from_env({"DATABASE_URL": "nonsense", "SECRET_KEY": "short", "PORT": "99999", "LOG_LEVEL": "loud"})
    text = str(info.value)
    for name in ("DATABASE_URL", "SECRET_KEY", "PORT", "LOG_LEVEL"):
        assert name in text, f"{name} is wrong and must be named in the error; got {text!r}. Collect all problems before raising."
    assert text.count("; ") == 3, f"Join the four problems with '; ' (3 separators); got {text!r}"


@pytest.mark.parametrize("port", ["0", "65536", "-1", "eighty", "80.5", " "])
def test_bad_ports(port):
    with pytest.raises(ConfigError, match="PORT"):
        Settings.from_env({**GOOD, "PORT": port})


@pytest.mark.parametrize("port, expected", [("1", 1), ("65535", 65535)])
def test_port_edges_are_allowed(port, expected):
    assert Settings.from_env({**GOOD, "PORT": port}).port == expected, "1 and 65535 are valid ports."


def test_secret_needs_32_characters():
    with pytest.raises(ConfigError, match="SECRET_KEY"):
        Settings.from_env({**GOOD, "SECRET_KEY": "k" * 31})
    assert Settings.from_env({**GOOD, "SECRET_KEY": "k" * 32}).secret_key == "k" * 32, "Exactly 32 characters is enough."


def test_bad_level_is_named():
    with pytest.raises(ConfigError, match="LOG_LEVEL"):
        Settings.from_env({**GOOD, "LOG_LEVEL": "LOUD"})


def test_repr_hides_the_secret():
    secret = "s3cr3t-" + "x" * 30
    shown = repr(Settings.from_env({**GOOD, "SECRET_KEY": secret}))
    assert secret not in shown, "repr() must never print the secret key: logs and tracebacks print settings objects."
    assert "***" in shown, "Show '***' in place of the secret."


def test_repr_hides_the_database_password():
    s = Settings.from_env({**GOOD, "DATABASE_URL": "postgresql://app:hunter2@db:5432/app"})
    shown = repr(s)
    assert "hunter2" not in shown, "The password inside DATABASE_URL must not appear in repr()."
    assert "postgresql://app:***@db:5432/app" in shown, f"Show the URL with the password replaced by ***; got {shown}"
    assert s.database_url == "postgresql://app:hunter2@db:5432/app", "Only the display hides the password; the value must stay intact."


def test_repr_keeps_a_url_without_password():
    shown = repr(Settings.from_env(GOOD))
    assert "sqlite:///dev.db" in shown, "A URL without a password is shown unchanged."
    assert "port=8000" in shown and "'INFO'" in shown, f"repr should show port and log level too; got {shown}"
