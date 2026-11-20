import csv
import io
import os


def build_report(rows, month):
    """Deterministic: sorted rows, a fixed header, no clock, no randomness."""
    out = io.StringIO()
    writer = csv.writer(out, lineterminator="\n")
    writer.writerow(["month", "order_id", "customer", "total_cents"])
    for order_id, customer, total in sorted(rows):
        writer.writerow([month, order_id, customer, total])
    return out.getvalue().encode("utf-8")


def write_atomic(path, data, crash=None):
    tmp = f"{path}.{os.getpid()}.tmp"                 # same folder, so os.replace is atomic
    with open(tmp, "wb") as f:
        f.write(data[: len(data) // 2])
        if crash:
            crash.hit("mid-write")
        f.write(data[len(data) // 2:])
        f.flush()
        os.fsync(f.fileno())                          # the bytes are on disk before the rename
    if crash:
        crash.hit("before-replace")
    os.replace(tmp, path)
