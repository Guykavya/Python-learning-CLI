"""Test setup for the Django problems: the same for all of them.

It builds a tiny Django "project" in memory (SQLite, no files), treats your solution.py as
the app called "shop", and creates the tables for the models you define there.
"""
import django
import pytest
from django.apps import AppConfig
from django.conf import settings


class ShopConfig(AppConfig):          # a fake app "shop" that owns the models of solution.py
    name = "conftest"
    label = "shop"


if not settings.configured:
    settings.configure(
        DEBUG=False,
        SECRET_KEY="test-secret-key-" + "0" * 40,
        ALLOWED_HOSTS=["testserver"],
        DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}},
        INSTALLED_APPS=[
            "django.contrib.admin", "django.contrib.auth", "django.contrib.contenttypes",
            "django.contrib.sessions", "django.contrib.messages", "rest_framework",
            "conftest.ShopConfig",
        ],
        MIDDLEWARE=[
            "django.contrib.sessions.middleware.SessionMiddleware",
            "django.middleware.common.CommonMiddleware",
            "django.middleware.csrf.CsrfViewMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware",
            "django.contrib.messages.middleware.MessageMiddleware",
        ],
        ROOT_URLCONF="solution",
        TEMPLATES=[{
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "APP_DIRS": True,
            "OPTIONS": {"context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]},
        }],
        USE_TZ=True,
        DEFAULT_AUTO_FIELD="django.db.models.BigAutoField",
        PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"],   # fast, tests only
    )
    django.setup()

from django.apps import apps            # noqa: E402
from django.core.management import call_command   # noqa: E402
from django.db import connection        # noqa: E402

import solution                         # noqa: E402,F401  (registers your models in the app "shop")

call_command("migrate", verbosity=0)    # tables of auth, admin, sessions, contenttypes
with connection.schema_editor() as editor:      # the tables of your own models (no migrations needed)
    for model in apps.get_app_config("shop").get_models():
        editor.create_model(model)


@pytest.fixture(autouse=True)
def _rollback():                        # every test starts from an empty database
    from django.db import transaction
    with transaction.atomic():
        yield
        transaction.set_rollback(True)
