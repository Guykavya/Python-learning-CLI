import csv
import io

from fastapi import FastAPI, HTTPException, UploadFile

MAX_BYTES = 1024 * 1024
CHUNK = 64 * 1024

app = FastAPI()


@app.post("/upload")
async def upload(file: UploadFile):
    # TODO: 415 unless text/csv; read in CHUNK pieces and 413 over MAX_BYTES;
    #       400 if not UTF-8; count non-empty rows after the header with csv.reader
    data = await file.read()                   # unsafe: reads everything at once
    return {"filename": file.filename, "rows": data.count(b"\n")}
