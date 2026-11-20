import csv
import io
import os


def build_report(rows, month):
    # TODO: header, then rows SORTED by order_id
    out = io.StringIO()
    writer = csv.writer(out, lineterminator="\n")
    for order_id, customer, total in rows:
        writer.writerow([month, order_id, customer, total])
    return out.getvalue().encode()


def write_atomic(path, data, crash=None):
    # NAIVE: the final file is visible (and truncated) as soon as it is opened. Make it atomic.
    with open(path, "wb") as f:
        f.write(data[: len(data) // 2])
        if crash:
            crash.hit("mid-write")
        f.write(data[len(data) // 2:])
