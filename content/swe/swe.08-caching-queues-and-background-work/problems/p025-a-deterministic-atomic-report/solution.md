## Approach

```python
import csv
import io
import os


def build_report(rows, month):
    out = io.StringIO()
    writer = csv.writer(out, lineterminator="\n")
    writer.writerow(["month", "order_id", "customer", "total_cents"])
    for order_id, customer, total in sorted(rows):
        writer.writerow([month, order_id, customer, total])
    return out.getvalue().encode("utf-8")


def write_atomic(path, data, crash=None):
    tmp = f"{path}.{os.getpid()}.tmp"
    with open(tmp, "wb") as f:
        f.write(data[: len(data) // 2])
        if crash:
            crash.hit("mid-write")
        f.write(data[len(data) // 2:])
        f.flush()
        os.fsync(f.fileno())
    if crash:
        crash.hit("before-replace")
    os.replace(tmp, path)
```

Determinism makes a rerun harmless (it overwrites the file with the same bytes); atomic publish makes a crash harmless (the final name only ever points to a complete file). Together the report job is idempotent without any log table.

## Cost

Writing the file twice (temporary, then a rename that costs almost nothing). `fsync` waits for the disk, typically milliseconds (machine-specific). Leftover `.tmp` files after crashes are harmless; a housekeeping job deletes old ones.

## Another way

`tempfile.NamedTemporaryFile(dir=folder, delete=False)` creates a unique temporary file in the same folder. For an expensive report, first check "does the final file already exist with the expected digest?" and skip the work. On object storage (S3) a single PUT is already atomic: upload under the final key in one request.
