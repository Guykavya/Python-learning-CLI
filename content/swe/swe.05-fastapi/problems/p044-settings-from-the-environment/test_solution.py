import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from solution import ConfigError, Settings, create_app

SECRET = "s" * 40
ALL = ("APP_DATABASE_URL", "APP_SECRET_KEY", "APP_DEBUG", "APP_TOKEN_MINUTES")


@pytest.fixture
def env(monkeypatch):
    for name in ALL:
        monkeypatch.delenv(name, raising=False)       # start from a clean environment
    return monkeypatch


def test_defaults_with_only_the_secret(env):
    env.setenv("APP_SECRET_KEY", SECRET)
    s = Settings.from_env()
    assert s.secret_key == SECRET, "from_env() without an argument must read os.environ."
    assert (s.database_url, s.debug, s.token_minutes) == ("sqlite:///./dev.db", False, 15), (
        f"Defaults are wrong: {s.database_url!r}, {s.debug!r}, {s.token_minutes!r}")


def test_strings_become_typed_values(env):
    env.setenv("APP_SECRET_KEY", SECRET)
    env.setenv("APP_DEBUG", "true")
    env.setenv("APP_TOKEN_MINUTES", "30")
    env.setenv("APP_DATABASE_URL", "postgresql://db/tasks")
    s = Settings.from_env()
    assert s.debug is True and s.token_minutes == 30, (
        f"'true' must become True and '30' must become 30 (got {s.debug!r}, {s.token_minutes!r}): declare the types bool and int.")
    assert s.database_url == "postgresql://db/tasks"


def test_a_plain_dict_also_works(env):
    s = Settings.from_env({"APP_SECRET_KEY": SECRET, "APP_DEBUG": "0"})
    assert s.debug is False, "from_env(environ) must read the mapping it is given."


def test_settings_are_frozen(env):
    s = Settings.from_env({"APP_SECRET_KEY": SECRET})
    with pytest.raises(ValidationError):
        s.debug = True                                # frozen models refuse assignment
    # (if this fails: add model_config = {"frozen": True})


def test_missing_secret_stops_the_app_at_startup(env):
    with pytest.raises(ConfigError) as info:
        create_app()
    message = str(info.value)
    assert "APP_SECRET_KEY" in message, (
        f"The error must name the environment variable APP_SECRET_KEY, got: {message!r}")


@pytest.mark.parametrize("name,value", [
    ("APP_DEBUG", "maybe"),
    ("APP_TOKEN_MINUTES", "abc"),
    ("APP_TOKEN_MINUTES", "0"),
    ("APP_TOKEN_MINUTES", "5000"),
])
def test_bad_values_are_refused(env, name, value):
    env.setenv("APP_SECRET_KEY", SECRET)
    env.setenv(name, value)
    with pytest.raises(ConfigError) as info:
        Settings.from_env()
    assert name in str(info.value), f"{name}={value!r} must be refused with a ConfigError naming {name}, got {str(info.value)!r}"


def test_every_problem_is_named_and_no_value_leaks(env):
    env.setenv("APP_SECRET_KEY", "short-but-secret")
    env.setenv("APP_TOKEN_MINUTES", "0")
    with pytest.raises(ConfigError) as info:
        Settings.from_env()
    message = str(info.value)
    assert "APP_SECRET_KEY" in message and "APP_TOKEN_MINUTES" in message, (
        f"Name every bad variable, not only the first: {message!r}")
    assert "short-but-secret" not in message, (
        "The secret's value appears in the error message (str(ValidationError) contains input_value). "
        "Build the message from loc and msg only, and raise ConfigError(...) from None.")
    assert info.value.__cause__ is None and info.value.__suppress_context__, (
        "Use 'raise ConfigError(...) from None', or the traceback will show the original ValidationError with the value.")


def test_info_route(env):
    env.setenv("APP_SECRET_KEY", SECRET)
    env.setenv("APP_DEBUG", "yes")
    with TestClient(create_app()) as client:
        body = client.get("/info").json()
    assert body == {"debug": True, "token_minutes": 15, "database": "sqlite"}, f"GET /info returned {body}"
    assert SECRET not in str(body), "Never return the secret."


def test_explicit_settings_win(env):
    s = Settings(secret_key="t" * 40, token_minutes=60)
    with TestClient(create_app(s)) as client:
        assert client.get("/info").json()["token_minutes"] == 60, (
            "create_app(settings) must use the settings it is given (tests pass them in) without reading the environment.")
