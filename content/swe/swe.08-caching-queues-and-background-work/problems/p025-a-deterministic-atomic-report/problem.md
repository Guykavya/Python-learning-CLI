# A deterministic, atomic report

Chapter section 11.8 (the report worker: deterministic and atomic). A report job writes a CSV file. Two rules make it safe to run twice and safe to crash:

1. **Deterministic output:** the same input always gives the same **bytes**. Sort the rows; take the month from the input; no "generated at" time, no random ids.
2. **Atomic publish:** write a temporary file **in the same folder**, flush it to disk, then `os.replace` it onto the final name. A reader sees the old complete file or the new complete file, never half of one.

## What to write

```python
def build_report(rows, month) -> bytes: ...
def write_atomic(path, data: bytes, crash=None) -> None: ...
```

- `rows` is a list of `(order_id, customer, total_cents)` tuples in any order. `build_report` returns UTF-8 bytes of a CSV with the header `month,order_id,customer,total_cents` and one line per row, **sorted by `order_id`**, using `csv.writer(..., lineterminator="\n")`. Every line starts with `month`.
- `write_atomic` writes `data` to a temporary file next to `path` whose name ends in `.tmp` (for example `f"{path}.{os.getpid()}.tmp"`), in two halves, calling `crash.hit("mid-write")` between them if `crash` is given. Then `flush()` and `os.fsync()`, then `crash.hit("before-replace")`, then `os.replace(tmp, path)`.

`crash.hit(point)` may raise `Crash` (the process dies). After a crash at either point, the **final file must be untouched**: still the old complete report, or absent if there was none.

## Example

```python
rows = [(3, "cy", 990), (1, "ada", 2500), (2, "bo", 4200)]
build_report(rows, "2026-10").decode()
# 'month,order_id,customer,total_cents\n2026-10,1,ada,2500\n2026-10,2,bo,4200\n2026-10,3,cy,990\n'
build_report(rows, "2026-10") == build_report(list(reversed(rows)), "2026-10")    # True
```
