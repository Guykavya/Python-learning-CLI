## Hint 1

Write the four rules as four separate steps, each one able to stop with an `HTTPException`. Which step needs no reading at all, so it should come first? In the reading loop: what does `await file.read(CHUNK)` return when the file is finished?

## Hint 2

```text
chunks, size = [], 0
loop:
    chunk = await file.read(CHUNK)
    if not chunk: break
    size += len(chunk)
    if size > MAX_BYTES: raise HTTPException(413, ...)
    chunks.append(chunk)
```
Keeping the chunks is fine here: you stop before more than `MAX_BYTES` is kept.

## Hint 3

```text
if file.content_type != "text/csv": raise HTTPException(415, "Only text/csv files are accepted")
read loop (hint 2)
try: text = b"".join(chunks).decode("utf-8")
except UnicodeDecodeError: raise HTTPException(400, "File is not UTF-8 text")
rows = list(csv.reader(io.StringIO(text)))
return {"filename": file.filename, "rows": count of non-empty rows in rows[1:]}
```
