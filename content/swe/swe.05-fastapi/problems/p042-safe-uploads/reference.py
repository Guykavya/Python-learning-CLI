import csv
import io

from fastapi import FastAPI, HTTPException, UploadFile

MAX_BYTES = 1024 * 1024
CHUNK = 64 * 1024

app = FastAPI()


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
