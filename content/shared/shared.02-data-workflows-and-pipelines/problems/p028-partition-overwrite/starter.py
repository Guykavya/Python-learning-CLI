import os
import shutil

import pyarrow as pa
import pyarrow.parquet as pq


def write_day(rows, root, day):
    """Replace the folder root/order_date=<day> with exactly these rows; leave other days alone."""
    raise NotImplementedError("check the days, write the new data first, then swap it in for the old folder")
