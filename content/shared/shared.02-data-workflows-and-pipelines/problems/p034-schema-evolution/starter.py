import pyarrow as pa
import pyarrow.parquet as pq


def evolve_table(conn, table, rows):
    """ALTER TABLE ... ADD COLUMN for every key of rows the table does not have; return the new names."""
    raise NotImplementedError("PRAGMA table_info, find new keys, check names and types, then ALTER TABLE")


def load_rows(conn, table, rows):
    """Evolve the table, then upsert every row by id with only the columns it has; return len(rows)."""
    raise NotImplementedError("evolve_table first, then INSERT ... ON CONFLICT(id) DO UPDATE per row")


def read_parquet_versions(paths):
    """Read old and new Parquet files into ONE table with the union of their columns."""
    raise NotImplementedError("unify the schemas (ValueError on a type conflict), then concatenate")
