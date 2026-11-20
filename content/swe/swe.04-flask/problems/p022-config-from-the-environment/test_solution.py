import pytest

from solution import create_app


@pytest.fixture(autouse=True)
def clean_environment(monkeypatch):
    for name in ("BLOG_PER_PAGE", "BLOG_TITLE", "BLOG_DEBUG", "BLOG_FEATURES__beta", "PER_PAGE", "DEBUG"):
        monkeypatch.delenv(name, raising=False)


def test_defaults():
    app = create_app()
    assert app.config["PER_PAGE"] == 10 and app.config["TITLE"] == "My Blog" and app.config["DEBUG"] is False


def test_numbers_become_ints(monkeypatch):
    monkeypatch.setenv("BLOG_PER_PAGE", "20")
    value = create_app().config["PER_PAGE"]
    assert value == 20 and isinstance(value, int), f"BLOG_PER_PAGE=20 must become the int 20, got {value!r}. Use app.config.from_prefixed_env('BLOG')."


def test_booleans_become_bools(monkeypatch):
    monkeypatch.setenv("BLOG_DEBUG", "true")
    assert create_app().config["DEBUG"] is True
    monkeypatch.setenv("BLOG_DEBUG", "false")
    assert create_app().config["DEBUG"] is False, "The string 'false' is truthy in Python; from_prefixed_env parses it as JSON to a real False."


def test_text_stays_text(monkeypatch):
    monkeypatch.setenv("BLOG_TITLE", "Hello World")
    assert create_app().config["TITLE"] == "Hello World", "Text that is not valid JSON stays a string."


def test_double_underscore_makes_a_nested_key(monkeypatch):
    monkeypatch.setenv("BLOG_FEATURES__beta", "true")
    assert create_app().config["FEATURES"] == {"beta": True}


def test_variables_without_the_prefix_are_ignored(monkeypatch):
    monkeypatch.setenv("PER_PAGE", "5")
    monkeypatch.setenv("DEBUG", "1")
    app = create_app()
    assert app.config["PER_PAGE"] == 10 and app.config["DEBUG"] is False, "Only BLOG_* variables may change the config."


def test_test_config_wins_over_the_environment(monkeypatch):
    monkeypatch.setenv("BLOG_PER_PAGE", "20")
    app = create_app({"PER_PAGE": 3})
    assert app.config["PER_PAGE"] == 3, "Apply test_config AFTER the environment."


def test_settings_route(monkeypatch):
    monkeypatch.setenv("BLOG_PER_PAGE", "25")
    monkeypatch.setenv("BLOG_TITLE", "Notes")
    data = create_app({"TESTING": True}).test_client().get("/settings").get_json()
    assert data == {"per_page": 25, "title": "Notes", "debug": False, "features": {"beta": False}}, f"got {data}"
