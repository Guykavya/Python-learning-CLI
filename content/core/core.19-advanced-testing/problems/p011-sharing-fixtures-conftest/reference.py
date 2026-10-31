CONFTEST = """
import pytest


@pytest.fixture
def app_config():
    return {"debug": False, "db": "memory"}


@pytest.fixture
def user(app_config):
    return {"name": "ada", "db": app_config["db"]}
"""

API_CONFTEST = """
import pytest


@pytest.fixture
def app_config():
    return {"debug": True, "db": "api-db"}
"""
