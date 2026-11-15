import sqlite3

import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from solution import evolve_table, load_rows, read_parquet_versions


@pytest.fixture
def conn():
    c = sqlite3.connect(":memory:")
    c.execute("CREATE TABLE orders (id INTEGER PRIMARY KEY, status TEXT, amount_cents INTEGER)")
    c.executemany("INSERT INTO orders VALUES (?, ?, ?)", [(1, "pending", 1999), (2, "shipped", 500)])
    c.commit()
    yield c
    c.close()


def columns(conn):
    return [(r[1], r[2]) for r in conn.execute("PRAGMA table_info(orders)")]


NEW_ROWS = [
    {"id": 3, "status": "shipped", "amount_cents": 700, "coupon": "JUNE10", "discount_cents": 70},
    {"id": 4, "status": "pending", "amount_cents": 100, "coupon": None, "gift_note": None},
]


# ---------- SQLite: evolve_table ----------

def test_adds_the_new_columns_in_first_seen_order(conn):
    added = evolve_table(conn, "orders", NEW_ROWS)
    assert added == ["coupon", "discount_cents", "gift_note"], (
        f"evolve_table returned {added}. Return the names of the columns it ADDED, in the order they "
        "first appear in the rows (row by row, key by key)."
    )
    assert columns(conn) == [
        ("id", "INTEGER"), ("status", "TEXT"), ("amount_cents", "INTEGER"),
        ("coupon", "TEXT"), ("discount_cents", "INTEGER"), ("gift_note", "TEXT"),
    ], f"Table columns are {columns(conn)}."


def test_type_comes_from_the_first_non_null_value(conn):
    rows = [{"id": 5, "rating": None}, {"id": 6, "rating": 4.5}, {"id": 7, "is_gift": True}]
    evolve_table(conn, "orders", rows)
    types = dict(columns(conn))
    assert types["rating"] == "REAL", (
        f"rating got type {types['rating']!r}. Skip None values: the first real value is 4.5, a float -> REAL."
    )
    assert types["is_gift"] == "INTEGER", "bool is stored as INTEGER in SQLite (0/1)."


def test_all_null_new_column_becomes_text(conn):
    evolve_table(conn, "orders", [{"id": 9, "gift_note": None}])
    assert dict(columns(conn))["gift_note"] == "TEXT", "A column with only None values gets type TEXT."


def test_old_rows_get_null_in_the_new_column(conn):
    evolve_table(conn, "orders", NEW_ROWS)
    got = conn.execute("SELECT id, coupon FROM orders ORDER BY id").fetchall()
    assert got == [(1, None), (2, None)], (
        f"Old rows read {got}. ALTER TABLE ADD COLUMN gives existing rows NULL; never rebuild or "
        "drop the table to add a column."
    )


def test_evolving_twice_adds_nothing_the_second_time(conn):
    evolve_table(conn, "orders", NEW_ROWS)
    again = evolve_table(conn, "orders", NEW_ROWS)
    assert again == [], (
        f"The second call returned {again}. Compare with the table's CURRENT columns "
        "(PRAGMA table_info) so a re-run does not try to add them again (duplicate column name)."
    )


def test_no_new_columns_returns_empty(conn):
    assert evolve_table(conn, "orders", [{"id": 1, "status": "x"}]) == []
    assert evolve_table(conn, "orders", []) == []


def test_unsafe_column_name_is_refused_and_nothing_changes(conn):
    rows = [{"id": 8, "coupon": "A", "x INTEGER); DROP TABLE orders; --": 1}]
    with pytest.raises(ValueError):
        evolve_table(conn, "orders", rows)
    assert [c for c, _ in columns(conn)] == ["id", "status", "amount_cents"], (
        "A bad name was found, but some columns were added anyway. Check every new name (and "
        "type) BEFORE the first ALTER TABLE. Column names cannot be ? parameters, so only "
        "str.isidentifier() names may be put into the SQL text."
    )


def test_unsupported_value_type_is_a_type_error(conn):
    with pytest.raises(TypeError) as info:
        evolve_table(conn, "orders", [{"id": 8, "items": [{"sku": "B1"}]}])
    assert "items" in str(info.value), "Name the column in the TypeError message."
    assert "items" not in [c for c, _ in columns(conn)]


# ---------- SQLite: load_rows ----------

def test_load_rows_inserts_new_rows_with_new_columns(conn):
    assert load_rows(conn, "orders", NEW_ROWS) == 2
    got = conn.execute("SELECT id, status, coupon, discount_cents, gift_note FROM orders ORDER BY id").fetchall()
    assert got == [
        (1, "pending", None, None, None),
        (2, "shipped", None, None, None),
        (3, "shipped", "JUNE10", 70, None),
        (4, "pending", None, None, None),
    ], f"Table after load_rows: {got}"


def test_load_rows_updates_existing_ids_only_in_given_columns(conn):
    load_rows(conn, "orders", [{"id": 1, "status": "shipped", "coupon": "LATE"}, {"id": 2, "status": "cancelled"}])
    got = conn.execute("SELECT id, status, amount_cents, coupon FROM orders ORDER BY id").fetchall()
    assert got == [(1, "shipped", 1999, "LATE"), (2, "cancelled", 500, None)], (
        f"Got {got}. An existing id is UPDATED (upsert), and only the columns present in the row "
        "change: amount_cents was not sent, so it keeps its old value."
    )
    assert conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0] == 2, "Upsert must not add a second row 1."


def test_load_rows_twice_is_idempotent(conn):
    load_rows(conn, "orders", NEW_ROWS)
    load_rows(conn, "orders", NEW_ROWS)
    assert conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0] == 4, (
        "Loading the same rows twice must not duplicate them."
    )


def test_load_rows_commits(tmp_path):
    path = tmp_path / "w.db"
    c = sqlite3.connect(path)
    c.execute("CREATE TABLE orders (id INTEGER PRIMARY KEY, status TEXT, amount_cents INTEGER)")
    c.commit()
    load_rows(c, "orders", NEW_ROWS)
    c.close()
    c2 = sqlite3.connect(path)
    n = c2.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    c2.close()
    assert n == 2, "The rows were not committed (use `with conn:` around the inserts)."


# ---------- Parquet: read_parquet_versions ----------

def write(path, data, schema):
    pq.write_table(pa.Table.from_pylist(data, schema=schema), path)
    return path


OLD = pa.schema([("id", pa.int64()), ("status", pa.string()), ("legacy_flag", pa.bool_())])
NEW = pa.schema([("id", pa.int64()), ("status", pa.string()), ("coupon", pa.string())])


def test_old_and_new_files_read_together(tmp_path):
    old = write(tmp_path / "old.parquet",
                [{"id": 1, "status": "pending", "legacy_flag": True}, {"id": 2, "status": "shipped", "legacy_flag": False}], OLD)
    new = write(tmp_path / "new.parquet", [{"id": 3, "status": "shipped", "coupon": "JUNE10"}], NEW)
    table = read_parquet_versions([old, new])
    assert table.schema.names == ["id", "status", "legacy_flag", "coupon"], (
        f"Columns are {table.schema.names}. The result has the union of the columns, in the order "
        "they first appear (old file first)."
    )
    assert table.to_pylist() == [
        {"id": 1, "status": "pending", "legacy_flag": True, "coupon": None},
        {"id": 2, "status": "shipped", "legacy_flag": False, "coupon": None},
        {"id": 3, "status": "shipped", "legacy_flag": None, "coupon": "JUNE10"},
    ], (
        f"Rows are {table.to_pylist()}. A column missing from a file is null for that file's rows "
        "(new columns in old files, removed columns in new files)."
    )
    assert table.schema.field("coupon").type == pa.string()
    assert table.schema.field("legacy_flag").type == pa.bool_()


def test_null_typed_column_is_compatible(tmp_path):
    a = write(tmp_path / "a.parquet", [{"id": 1, "coupon": None}],
              pa.schema([("id", pa.int64()), ("coupon", pa.null())]))
    b = write(tmp_path / "b.parquet", [{"id": 2, "coupon": "X"}], pa.schema([("id", pa.int64()), ("coupon", pa.string())]))
    table = read_parquet_versions([a, b])
    assert table.schema.field("coupon").type == pa.string(), (
        "A column of type null (all values missing when it was written) fits any type; the "
        "result takes the real type, string."
    )
    assert table.column("coupon").to_pylist() == [None, "X"]


def test_conflicting_types_raise_value_error_naming_the_column(tmp_path):
    a = write(tmp_path / "a.parquet", [{"id": 1, "amount": 1999}], pa.schema([("id", pa.int64()), ("amount", pa.int64())]))
    b = write(tmp_path / "b.parquet", [{"id": 2, "amount": "19.99"}], pa.schema([("id", pa.int64()), ("amount", pa.string())]))
    with pytest.raises(ValueError) as info:
        read_parquet_versions([a, b])
    assert "amount" in str(info.value), (
        f"The message {str(info.value)!r} must name the column whose types disagree."
    )


def test_int32_vs_int64_is_also_a_conflict(tmp_path):
    a = write(tmp_path / "a.parquet", [{"id": 1}], pa.schema([("id", pa.int64())]))
    b = write(tmp_path / "b.parquet", [{"id": 2}], pa.schema([("id", pa.int32())]))
    with pytest.raises(ValueError):
        read_parquet_versions([a, b])
    # Do not cast silently: a type change in the source is something a person should look at.


def test_three_versions_and_one_file(tmp_path):
    v1 = write(tmp_path / "v1.parquet", [{"id": 1}], pa.schema([("id", pa.int64())]))
    v2 = write(tmp_path / "v2.parquet", [{"id": 2, "coupon": "A"}], NEW.remove(1))
    v3 = write(tmp_path / "v3.parquet", [{"id": 3, "city": "Pune"}], pa.schema([("id", pa.int64()), ("city", pa.string())]))
    table = read_parquet_versions([v1, v2, v3])
    assert table.schema.names == ["id", "coupon", "city"]
    assert table.to_pylist() == [
        {"id": 1, "coupon": None, "city": None},
        {"id": 2, "coupon": "A", "city": None},
        {"id": 3, "coupon": None, "city": "Pune"},
    ]
    assert read_parquet_versions([v1]).to_pylist() == [{"id": 1}], "One file reads as itself."


def test_no_files_is_an_error():
    with pytest.raises(ValueError):
        read_parquet_versions([])
