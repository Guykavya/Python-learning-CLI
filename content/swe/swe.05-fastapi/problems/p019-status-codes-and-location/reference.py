from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel

app = FastAPI()
NOTES = {}          # id -> text


class NoteIn(BaseModel):
    text: str


@app.post("/notes", status_code=status.HTTP_201_CREATED)
def create_note(data: NoteIn, response: Response):
    if data.text in NOTES.values():
        raise HTTPException(status.HTTP_409_CONFLICT, "Note already exists")
    note_id = max(NOTES, default=0) + 1
    NOTES[note_id] = data.text
    response.headers["Location"] = f"/notes/{note_id}"
    return {"id": note_id, "text": data.text}


@app.get("/notes/{note_id}")
def get_note(note_id: int):
    if note_id not in NOTES:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Note not found")
    return {"id": note_id, "text": NOTES[note_id]}


@app.delete("/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(note_id: int):
    if note_id not in NOTES:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Note not found")
    del NOTES[note_id]
