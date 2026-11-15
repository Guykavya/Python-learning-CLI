import pyarrow as pa
import pyarrow.parquet as pq

# Build the schema once, at module level, with pa.schema([...]) and pa.field(name, type, nullable=...).
ORDER_SCHEMA = None


def write_orders(rows, path):
    """Write rows to a Parquet file with ORDER_SCHEMA; return the number of rows."""
    raise NotImplementedError("reject naive datetimes, build a table with the schema, write it")


def read_orders(path):
    """Read the Parquet file back as a list of plain Python dicts."""
    raise NotImplementedError("read the table and turn it into a list of dicts")
