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


def setup(tmp_path):
    return make_config(tmp_path, [("0001", None, from_solution(("upgrade_0001", "downgrade_0001")))])


def test_upgrade_creates_the_table(tmp_path):
    cfg, db = setup(tmp_path)
    command.upgrade(cfg, "head")
    cols = columns(db, "products")
    assert set(cols) == {"id", "name", "price_paise"}, f"Columns of products: {sorted(cols)}"
    assert cols["name"]["notnull"] and cols["price_paise"]["notnull"], "name and price_paise must be NOT NULL."
    assert cols["price_paise"]["type"] == "INTEGER" and cols["name"]["type"].startswith("VARCHAR")
    assert rows(db, "SELECT version_num FROM alembic_version") == [("0001",)]


def test_not_null_is_enforced(tmp_path):
    cfg, db = setup(tmp_path)
    command.upgrade(cfg, "head")
    c = sqlite3.connect(db)
    with pytest.raises(sqlite3.IntegrityError, match="NOT NULL"):
        c.execute("INSERT INTO products(name, price_paise) VALUES (NULL, 100)")


def test_downgrade_removes_the_table(tmp_path):
    cfg, db = setup(tmp_path)
    command.upgrade(cfg, "head")
    command.downgrade(cfg, "base")
    tables = {r[0] for r in rows(db, "SELECT name FROM sqlite_master WHERE type='table'")}
    assert "products" not in tables, "downgrade base must drop the products table."
    assert rows(db, "SELECT COUNT(*) FROM alembic_version") == [(0,)]


def test_upgrade_again_after_a_downgrade(tmp_path):
    cfg, db = setup(tmp_path)
    command.upgrade(cfg, "head")
    command.downgrade(cfg, "base")
    command.upgrade(cfg, "head")
    assert set(columns(db, "products")) == {"id", "name", "price_paise"}, "A clean downgrade lets you upgrade again."
