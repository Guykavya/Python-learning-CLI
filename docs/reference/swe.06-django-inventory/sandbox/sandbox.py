import django
from django.apps import AppConfig
from django.conf import settings


class ShopConfig(AppConfig):
    """A fake app called "shop" so that our models belong to a registered app."""
    name = "sandbox"
    label = "shop"


if not settings.configured:
    settings.configure(
        DEBUG=False,
        SECRET_KEY="sandbox-secret-key-for-demos-only-0000000000000000",
        DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}},
        INSTALLED_APPS=["django.contrib.contenttypes", "django.contrib.auth", "sandbox.ShopConfig"],
        USE_TZ=True,
    )
    django.setup()

from django.db import connection, models
from django.test.utils import CaptureQueriesContext


def create_tables(*model_classes):
    """Create one table per model (parents first). Migrations do this in a real project."""
    with connection.schema_editor() as editor:
        for model in model_classes:
            editor.create_model(model)


class show_queries:
    """Context manager: print how many SQL queries ran, and the SQL text."""

    def __init__(self, label=""):
        self.label = label

    def __enter__(self):
        self.ctx = CaptureQueriesContext(connection)
        self.ctx.__enter__()
        return self.ctx

    def __exit__(self, *exc):
        self.ctx.__exit__(*exc)
        n = len(self.ctx.captured_queries)
        print(f"{self.label}{n} quer{'y' if n == 1 else 'ies'}")
        for q in self.ctx.captured_queries:
            print("  ", q["sql"])
