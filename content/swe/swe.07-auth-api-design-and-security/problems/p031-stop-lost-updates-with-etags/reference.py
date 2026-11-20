import hashlib
import threading

from fastapi import FastAPI, Header, HTTPException, Response
from pydantic import BaseModel


class NoteIn(BaseModel):
    note: str


def etag_of(version):
    digest = hashlib.sha256(f"version-{version}".encode()).hexdigest()[:16]
    return f'"{digest}"'


def build_app(seed):
    app = FastAPI()
    notes = {note_id: {"note": text, "version": 1} for note_id, text in seed.items()}
    lock = threading.Lock()

    @app.get("/notes/{note_id}")
    def read_note(note_id: int, response: Response):
        item = notes.get(note_id)
        if item is None:
            raise HTTPException(404, "no such note")
        response.headers["ETag"] = etag_of(item["version"])
        return {"id": note_id, "note": item["note"]}

    @app.put("/notes/{note_id}")
    def write_note(note_id: int, body: NoteIn, response: Response, if_match: str | None = Header(default=None)):
        with lock:                                              # compare and write as ONE step
            item = notes.get(note_id)
            if item is None:
                raise HTTPException(404, "no such note")
            if if_match is None:
                raise HTTPException(428, "send If-Match with the ETag you last read")
            if if_match != etag_of(item["version"]):
                raise HTTPException(412, "the note changed; reload and try again")
            item["note"] = body.note
            item["version"] += 1
            response.headers["ETag"] = etag_of(item["version"])
            return {"id": note_id, "note": item["note"]}

    return app
