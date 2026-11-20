## Approach

```python
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
```

The ETag is derived from the version, and the version only goes up, so an old ETag can never match again. `428` says "I cannot accept a write without a precondition"; `412` says "your precondition is false". The lock plays the role of the chapter's `UPDATE ... WHERE version = ?`: with a real database you would put the version in the `WHERE` clause and look at `rowcount`, so that the database does the compare-and-write atomically.

When the client gets a `412` it reloads, shows the other person's change, merges, and tries again with the new ETag. The server never decides how to merge.

## Complexity

O(1) per request. The lock serialises writers only for the short compare-and-write.

## Another way

Instead of hashing the version you can use a content hash of the whole note (`sha256(text)`): then two writers who save the *same* text produce the same ETag. A version number is cheaper and also detects "changed and changed back" (A to B to A), which a content hash cannot see. A third option is a `version` or `updated_at` field in the JSON body, which works but is not standard HTTP.
