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
    op.execute("CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT NOT NULL, price REAL)")

def downgrade():
    op.execute("DROP TABLE products")
"""
PRICES = [12.30, 99.99, 0.07, 1000000.01, 0.1, 19.9, 5.0, 0.29, 4.35, 8.2]
STEPS = [("0002", ("upgrade_0002", "downgrade_0002")), ("0003", ("upgrade_0003", "downgrade_0003")), ("0004", ("upgrade_0004", "downgrade_0004"))]


@pytest.fixture
def env(tmp_path):
    revs = [("0001", None, REV1)]
    down = "0001"
    for rev, names in STEPS:
        revs.append((rev, down, from_solution(names)))
        down = rev
    cfg, db = make_config(tmp_path, revs)
    command.upgrade(cfg, "0001")
    c = sqlite3.connect(db)
    c.executemany("INSERT INTO products(name, price) VALUES (?, ?)", [(f"p{i}", v) for i, v in enumerate(PRICES)])
    c.commit()
    c.close()
    return cfg, db


def paise(db):
    return [r[0] for r in rows(db, "SELECT price_paise FROM products ORDER BY id")]


def test_expand_adds_a_nullable_column_and_old_code_still_works(env):
    cfg, db = env
    command.upgrade(cfg, "0002")
    cols = columns(db, "products")
    assert "price_paise" in cols and not cols["price_paise"]["notnull"], "Expand: add price_paise as a NULLABLE column."
    assert "price" in cols, "Expand must not remove the old column."
    c = sqlite3.connect(db)
    c.execute("INSERT INTO products(name, price) VALUES ('written by old code', 3.5)")
    c.commit()
    assert paise(db)[-1] is None


def test_backfill_gives_exact_integers_including_late_rows(env):
    cfg, db = env
    command.upgrade(cfg, "0002")
    c = sqlite3.connect(db)
    c.execute("INSERT INTO products(name, price) VALUES ('late', 3.5)")
    c.commit()
    c.close()
    command.upgrade(cfg, "0003")
    assert paise(db) == [1230, 9999, 7, 100000001, 10, 1990, 500, 29, 435, 820, 350], (
        f"Got {paise(db)}. price_paise = round(price * 100): 99.99 must give 9999, not 9998.")
    assert [r[0] for r in rows(db, "SELECT price FROM products ORDER BY id")][:3] == [12.3, 99.99, 0.07], "The old column is untouched."


def test_backfill_works_in_batches_on_many_rows(env):
    cfg, db = env
    command.upgrade(cfg, "0002")
    c = sqlite3.connect(db)
    c.executemany("INSERT INTO products(name, price) VALUES (?, ?)", [(f"bulk{i}", i / 100) for i in range(1, 1301)])
    c.commit()
    c.close()
    command.upgrade(cfg, "0003")
    assert rows(db, "SELECT COUNT(*) FROM products WHERE price_paise IS NULL") == [(0,)], "Every row (also beyond one batch of 500) must be filled."
    assert rows(db, "SELECT price_paise FROM products WHERE name = 'bulk1300'") == [(1300,)]
    assert rows(db, "SELECT COUNT(*) FROM products WHERE price_paise <> CAST(ROUND(price * 100) AS INTEGER)") == [(0,)]


def test_contract_drops_the_old_column(env):
    cfg, db = env
    command.upgrade(cfg, "head")
    cols = columns(db, "products")
    assert "price" not in cols, "Contract: the old column must be gone."
    assert cols["price_paise"]["notnull"] and cols["price_paise"]["type"] == "INTEGER"
    assert paise(db) == [1230, 9999, 7, 100000001, 10, 1990, 500, 29, 435, 820]
    assert [r[0] for r in rows(db, "SELECT name FROM products ORDER BY id")][:2] == ["p0", "p1"], "Other columns survive."


def test_downgrade_restores_the_rupee_prices_exactly(env):
    cfg, db = env
    command.upgrade(cfg, "head")
    command.downgrade(cfg, "0003")
    cols = columns(db, "products")
    assert "price" in cols and not cols["price_paise"]["notnull"], "downgrade 0004 brings back price and makes price_paise nullable."
    assert [r[0] for r in rows(db, "SELECT price FROM products ORDER BY id")] == PRICES, "Every rupee value must come back exactly."
    command.downgrade(cfg, "0002")
    assert paise(db) == [None] * len(PRICES), "downgrade 0003 clears the backfill."
    command.downgrade(cfg, "0001")
    assert "price_paise" not in columns(db, "products")
    assert [r[0] for r in rows(db, "SELECT price FROM products ORDER BY id")] == PRICES


def test_the_whole_cycle_twice(env):
    cfg, db = env
    for _ in range(2):
        command.upgrade(cfg, "head")
        assert paise(db) == [1230, 9999, 7, 100000001, 10, 1990, 500, 29, 435, 820]
        command.downgrade(cfg, "base" if False else "0001")
        assert [r[0] for r in rows(db, "SELECT price FROM products ORDER BY id")] == PRICES
