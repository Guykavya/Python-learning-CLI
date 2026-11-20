import pytest

from solution import Config, create_app


def test_testing_config():
    app = create_app("testing")
    assert app.testing is True and app.config["SECRET_KEY"] == "test-key", "TestingConfig sets TESTING=True and SECRET_KEY='test-key'."
    assert app.debug is False


def test_development_config():
    app = create_app("development")
    assert app.debug is True and app.config["SECRET_KEY"] == "dev-key"


def test_default_is_development():
    assert create_app().debug is True, "create_app() with no argument uses 'development'."


def test_unknown_name():
    with pytest.raises(ValueError):
        create_app("staging")


def test_production_needs_a_real_secret_key(monkeypatch):
    monkeypatch.delenv("SECRET_KEY", raising=False)
    with pytest.raises(RuntimeError):
        create_app("production")
    monkeypatch.setenv("SECRET_KEY", "")
    with pytest.raises(RuntimeError):
        create_app("production")
    monkeypatch.setenv("SECRET_KEY", "change-me")
    with pytest.raises(RuntimeError):
        create_app("production")


def test_production_with_a_key(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "a-long-random-value-1234567890")
    app = create_app("production")
    assert app.config["SECRET_KEY"] == "a-long-random-value-1234567890", "In production the key comes from the SECRET_KEY environment variable."
    assert app.debug is False and app.testing is False


def test_development_and_testing_do_not_need_the_environment(monkeypatch):
    monkeypatch.delenv("SECRET_KEY", raising=False)
    create_app("development")
    create_app("testing")


def test_two_apps_do_not_share_settings():
    a, b = create_app("testing"), create_app("testing")
    a.config["FEATURES"]["beta"] = True
    a.config["PER_PAGE"] = 99
    assert b.config["FEATURES"] == {"beta": False}, "The apps share the FEATURES dict: from_object copies references. Deep-copy the values."
    assert b.config["PER_PAGE"] == 10
    assert Config.FEATURES == {"beta": False}, "The CLASS was changed through an app's config: copy the values so the class stays untouched."


def test_config_route(monkeypatch):
    client = create_app("testing").test_client()
    assert client.get("/config").get_json() == {"name": "testing", "debug": False, "testing": True, "per_page": 10}
    assert create_app("development").test_client().get("/config").get_json()["debug"] is True
