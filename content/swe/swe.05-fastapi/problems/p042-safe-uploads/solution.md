## Approach

Cheap checks first, then a bounded read, then parsing.

```python
@app.post("/upload")
async def upload(file: UploadFile):
    if file.content_type != "text/csv":
        raise HTTPException(415, "Only text/csv files are accepted")

    chunks = []
    size = 0
    while True:
        chunk = await file.read(CHUNK)                 # at most CHUNK bytes at a time
        if not chunk:
            break
        size += len(chunk)
        if size > MAX_BYTES:
            raise HTTPException(413, f"File larger than {MAX_BYTES} bytes")
        chunks.append(chunk)                           # bounded: never more than MAX_BYTES kept

    try:
        text = b"".join(chunks).decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(400, "File is not UTF-8 text")

    rows = list(csv.reader(io.StringIO(text)))
    data_rows = [row for row in rows[1:] if row]       # skip the header and blank lines
    return {"filename": file.filename, "rows": len(data_rows)}
```

Example: a 3 MiB upload. The loop reads 64 KiB at a time; after 17 reads the total is 1,114,112 bytes, which is over 1,048,576, so the endpoint answers 413 having held at most about 1 MiB. With `await file.read()` it would have loaded all 3 MiB (or 3 GiB) first and only then compared.

Example of the CSV rule: `id,title\n1,"two\nlines"\n\n2,x\n` has 5 newline characters, but `csv.reader` gives `["id","title"]`, `["1","two\nlines"]`, `[]`, `["2","x"]`: after the header and without the empty row, 2 rows.

The status codes: **415 Unsupported Media Type** (wrong kind of content), **413 Payload Too Large** (too big), **400 Bad Request** (the content itself is broken).

## Complexity

O(n) time for a file of n bytes, and O(min(n, MAX_BYTES)) memory in your code: you never keep more than the limit.

## Another way

Count rows **while** reading, without keeping the chunks: decode with an incremental decoder (`codecs.getincrementaldecoder("utf-8")()`) and feed the text pieces to a line-based parser. That keeps memory at O(CHUNK) and allows much larger limits (for example 100 MB files written to disk). Also remember that `content_type` is chosen by the **client**, so it is only a first filter: check the content itself (here, that it decodes and parses) before trusting it, and never use `file.filename` as a path on disk (section 16).
