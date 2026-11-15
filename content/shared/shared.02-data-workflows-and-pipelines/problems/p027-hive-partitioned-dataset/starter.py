import pyarrow as pa
import pyarrow.parquet as pq


def write_partitioned(rows, root):
    """Write rows under root as root/order_date=YYYY-MM-DD/*.parquet; return the sorted days."""
    raise NotImplementedError("add an order_date column (UTC day), then pq.write_to_dataset(..., partition_cols=[...])")


def read_partition(root, day):
    """Read only the files of one day; return its rows (five columns) sorted by id."""
    raise NotImplementedError("read just root/order_date=<day>, or filter on order_date")
