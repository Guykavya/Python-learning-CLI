import sqlite3
import textwrap

from alembic import command
from alembic.config import Config

ENV = """
from alembic import context
from sqlalchemy import create_engine

engine = create_engine(context.config.get_main_option("sqlalchemy.url"))
with engine.connect() as connection:
    context.configure(connection=connection, target_metadata=None)
    with context.begin_transaction():
        context.run_migrations()
"""


def make_config(tmp_path, revisions):
    """revisions: list of (revision, down_revision, python source of the file body)."""
    script = tmp_path / "alembic_scripts"
    (script / "versions").mkdir(parents=True)
    (script / "env.py").write_text(ENV, encoding="utf-8")
    (script / "script.py.mako").write_text("", encoding="utf-8")
    for rev, down, body in revisions:
        header = f'revision = "{rev}"\ndown_revision = {down!r}\nbranch_labels = None\ndepends_on = None\n'
        (script / "versions" / f"{rev}.py").write_text(header + textwrap.dedent(body), encoding="utf-8")
    cfg = Config()
    cfg.set_main_option("script_location", str(script))
    cfg.set_main_option("sqlalchemy.url", f"sqlite:///{tmp_path / 'app.db'}")
    return cfg, tmp_path / "app.db"


def from_solution(names):
    up, down = names
    return f"from solution import {up} as _up, {down} as _down\n\ndef upgrade():\n    _up()\n\ndef downgrade():\n    _down()\n"


def rows(db_path, sql):
    c = sqlite3.connect(db_path)
    try:
        return c.execute(sql).fetchall()
    finally:
        c.close()


def columns(db_path, table):
    return {r[1]: {"type": r[2].upper(), "notnull": bool(r[3])} for r in sqlite3.connect(db_path).execute(f"PRAGMA table_info({table})")}



import sqlite3

import pytest
from alembic import command

REV1 = """
from alembic import op

def upgrade():
    op.execute("CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT NOT NULL)")

def downgrade():
    op.execute("DROP TABLE products")
"""


def setup(tmp_path):
    cfg, db = make_config(tmp_path, [("0001", None, REV1), ("0002", "0001", from_solution(("upgrade_0002", "downgrade_0002")))])
    command.upgrade(cfg, "0001")
    c = sqlite3.connect(db)
    c.executemany("INSERT INTO products(name) VALUES (?)", [("Green Tea",), ("  Big   Mug ",), ("Cup",)])
    c.commit()
    c.close()
    return cfg, db


def test_existing_rows_get_a_slug_and_keep_their_data(tmp_path):
    cfg, db = setup(tmp_path)
    command.upgrade(cfg, "head")
    assert rows(db, "SELECT id, name, slug FROM products ORDER BY id") == [
        (1, "Green Tea", "green-tea"), (2, "  Big   Mug ", "big-mug"), (3, "Cup", "cup")], (
        "Every existing row keeps its id and name and gets slug = lower-cased name, white space runs replaced by '-'.")


def test_the_column_is_not_null_afterwards(tmp_path):
    cfg, db = setup(tmp_path)
    command.upgrade(cfg, "head")
    cols = columns(db, "products")
    assert cols["slug"]["notnull"], "After the backfill the column must be NOT NULL (batch mode alter_column)."
    assert cols["slug"]["type"].startswith("VARCHAR")
    c = sqlite3.connect(db)
    with pytest.raises(sqlite3.IntegrityError, match="NOT NULL"):
        c.execute("INSERT INTO products(name) VALUES ('no slug')")


def test_upgrade_works_on_an_empty_table(tmp_path):
    cfg, db = make_config(tmp_path, [("0001", None, REV1), ("0002", "0001", from_solution(("upgrade_0002", "downgrade_0002")))])
    command.upgrade(cfg, "head")
    assert rows(db, "SELECT COUNT(*) FROM products") == [(0,)] and columns(db, "products")["slug"]["notnull"]


def test_downgrade_removes_the_column_and_keeps_the_rows(tmp_path):
    cfg, db = setup(tmp_path)
    command.upgrade(cfg, "head")
    command.downgrade(cfg, "-1")
    assert "slug" not in columns(db, "products")
    assert rows(db, "SELECT id, name FROM products ORDER BY id") == [(1, "Green Tea"), (2, "  Big   Mug "), (3, "Cup")]
    assert rows(db, "SELECT version_num FROM alembic_version") == [("0001",)]


def test_upgrade_downgrade_upgrade(tmp_path):
    cfg, db = setup(tmp_path)
    command.upgrade(cfg, "head")
    command.downgrade(cfg, "-1")
    command.upgrade(cfg, "head")
    assert rows(db, "SELECT slug FROM products ORDER BY id") == [("green-tea",), ("big-mug",), ("cup",)]
