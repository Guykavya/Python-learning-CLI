# Safe uploads

Chapter section 16. Users upload a CSV file of tasks; the API answers how many rows it has. An upload endpoint is an open door: someone can send a 2 GB file, or a picture called `tasks.csv`. Write `POST /upload` in `solution.py` that is safe against both.

File uploads (`multipart/form-data`) need the package **python-multipart**. It is a course dependency, so it is installed (chapter section 16). Declare the parameter as `file: UploadFile`. The useful parts of an `UploadFile`: `file.filename`, `file.content_type`, and `await file.read(size)`, which returns **at most** `size` bytes (and `b""` at the end of the file).

Rules, checked in this order:

1. **Type.** If `file.content_type` is not exactly `"text/csv"`: **415** with detail `"Only text/csv files are accepted"`.
2. **Size, read in chunks.** Read with `await file.read(CHUNK)` (`CHUNK = 64 * 1024`, given) in a loop, adding up the bytes. As soon as the total goes over `MAX_BYTES = 1024 * 1024` (1 MiB, given), stop reading and answer **413** with detail `"File larger than 1048576 bytes"`. Exactly `MAX_BYTES` is allowed. **Never** call `file.read()` without a size: that loads the whole upload into memory at once, whatever its size (the tests check this).
3. **Text.** Decode the collected bytes as UTF-8. If that fails: **400** with detail `"File is not UTF-8 text"`.
4. **Count.** Parse the text with `csv.reader(io.StringIO(text))` (core module on files and CSV). The first row is the header. Count the remaining rows that are **not empty** (a blank line gives an empty row `[]`). Answer **200** `{"filename": ..., "rows": N}`. A header-only file has 0 rows.

Why `csv.reader` and not counting `\n`? A CSV value in quotes may contain a line break: `1,"buy milk\nand bread"` is **one** row on two lines.

## Example

```text
tasks.csv  text/csv  "id,title\n1,write\n2,test\n"             -> 200 {"filename": "tasks.csv", "rows": 2}
notes.csv  text/csv  "id,title\n1,\"two\nlines\"\n\n"          -> 200 {"filename": "notes.csv", "rows": 1}
cat.png    image/png ...                                       -> 415
big.csv    text/csv  1 MiB + 1 byte                            -> 413
bad.csv    text/csv  b"\xff\xfe..."                            -> 400
```

How the tests upload: `client.post("/upload", files={"file": ("tasks.csv", b"id,title\n1,write\n", "text/csv")})`.

Honest note: python-multipart already stores the upload in a temporary file (in memory up to 1 MiB, then on disk) before your endpoint runs. Reading in chunks protects **your** process's memory; to stop huge uploads before they arrive at all, set a body size limit in the server or the proxy in front of it (section 21).
