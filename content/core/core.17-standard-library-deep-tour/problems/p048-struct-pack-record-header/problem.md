# A binary file format with `struct`

Text formats (CSV, JSON) are easy to read but big and slow to parse. Many real formats (images, sound,
network packets, game saves) store numbers as **raw bytes** in fixed places. The `struct` module packs
Python values into such bytes and unpacks them again, following a *format string*:

| Code | Meaning | Bytes |
|---|---|---|
| `<` | little-endian, **no padding** (put it first) | |
| `4s` | 4 raw bytes | 4 |
| `H` | unsigned 16-bit int | 2 |
| `I` | unsigned 32-bit int | 4 |
| `q` | signed 64-bit int | 8 |
| `d` | 64-bit float | 8 |
| `8s` | 8 raw bytes (shorter values are padded with `\x00`, **longer ones are silently cut**) | 8 |

Without `<`, struct uses the native order **and inserts padding** for alignment, so the size changes
between computers. Always start a file format with `<` or `>`.

## The format

A file is a 20-byte **header** followed by `count` records of 20 bytes each.

- Header, format `"<4sHHIq"`: magic `b"KVLG"`, `version`, `flags`, `count`, `timestamp` (seconds).
- Record, format `"<Id8s"`: `id` (unsigned 32-bit), `value` (float), `name` (UTF-8, at most 8 bytes).

## Your task

In `solution.py`, define the constants `HEADER = "<4sHHIq"`, `RECORD = "<Id8s"`, `MAGIC = b"KVLG"` and:

1. `pack_header(version, flags, count, timestamp) -> bytes` (20 bytes).
2. `unpack_header(data) -> dict` with the keys `"version"`, `"flags"`, `"count"`, `"timestamp"`.
   Only the first 20 bytes are read. Raise `ValueError` if `data` is shorter than 20 bytes or the magic
   is not `b"KVLG"`.
3. `pack_record(rec_id, value, name) -> bytes` (20 bytes). Raise `ValueError` if the UTF-8 name is
   longer than 8 **bytes** (do not let struct cut it). Out-of-range numbers (a negative id) may raise
   `struct.error` from `struct.pack`: let it happen.
4. `unpack_record(data) -> tuple[int, float, str]`: remove the `\x00` padding from the name and
   decode it.
5. `write_file(path, records, timestamp, version=1, flags=0)`: write the header (with `count` =
   number of records) and all records. `records` is a list of `(id, value, name)` tuples.
6. `read_file(path) -> tuple[dict, list[tuple[int, float, str]]]`: the header dict and the records.
   Raise `ValueError` if the length of the data after the header is not exactly `count * 20` (a
   truncated or damaged file). `struct.iter_unpack(RECORD, data)` unpacks many records at once.

**Example**

```python
pack_header(1, 3, 2, 1700000000).hex(" ")
# '4b 56 4c 47 01 00 03 00 02 00 00 00 00 f1 53 65 00 00 00 00'
#   K  V  L  G  version flags  count        timestamp (little-endian)

pack_record(7, 2.5, "pen").hex(" ")
# '07 00 00 00 00 00 00 00 00 00 04 40 70 65 6e 00 00 00 00 00'
#   id=7         value=2.5                p  e  n  (padding)

unpack_record(pack_record(7, 2.5, "pen"))      # (7, 2.5, 'pen')
struct.calcsize("Id8s")                        # 24 on a typical PC: native alignment adds 4 padding bytes
```
