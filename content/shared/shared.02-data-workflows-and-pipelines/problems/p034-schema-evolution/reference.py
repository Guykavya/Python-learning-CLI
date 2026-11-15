import pyarrow as pa
import pyarrow.parquet as pq

SQL_TYPES = {bool: "INTEGER", int: "INTEGER", float: "REAL", str: "TEXT"}


def check_name(name):
    if not isinstance(name, str) or not name.isidentifier():
        raise ValueError(f"not a safe column or table name: {name!r}")


def existing_columns(conn, table):
    check_name(table)
    return [row[1] for row in conn.execute(f"PRAGMA table_info({table})")]


def sql_type(values, name):
    for value in values:
        if value is not None:
            if type(value) not in SQL_TYPES:
                raise TypeError(f"column {name}: cannot store {type(value).__name__}")
            return SQL_TYPES[type(value)]
    return "TEXT"


def evolve_table(conn, table, rows):
    have = existing_columns(conn, table)
    new = []
    for row in rows:
        for name in row:
            if name not in have and name not in new:
                new.append(name)
    # Check everything before changing anything.
    plan = []
    for name in new:
        check_name(name)
        plan.append((name, sql_type([row.get(name) for row in rows], name)))
    for name, kind in plan:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {name} {kind}")
    conn.commit()
    return new


def load_rows(conn, table, rows):
    evolve_table(conn, table, rows)
    with conn:
        for row in rows:
            names = list(row)
            placeholders = ", ".join("?" for _ in names)
            updates = ", ".join(f"{n} = excluded.{n}" for n in names if n != "id")
            sql = f"INSERT INTO {table} ({', '.join(names)}) VALUES ({placeholders})"
            sql += f" ON CONFLICT(id) DO UPDATE SET {updates}" if updates else " ON CONFLICT(id) DO NOTHING"
            conn.execute(sql, [row[n] for n in names])
    return len(rows)


def read_parquet_versions(paths):
    if not paths:
        raise ValueError("no files to read")
    tables = [pq.read_table(path) for path in paths]
    try:
        pa.unify_schemas([t.schema for t in tables])
    except (pa.ArrowTypeError, pa.ArrowInvalid) as error:
        raise ValueError(f"files disagree on a column type: {error}") from error
    return pa.concat_tables(tables, promote_options="default")
