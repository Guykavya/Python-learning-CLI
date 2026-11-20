from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel

app = FastAPI()
NOTES = {}          # id -> text


class NoteIn(BaseModel):
    text: str


@app.post("/notes")
def create_note(data: NoteIn, response: Response):
    # TODO: 409 for a duplicate text, 201 + Location header for a new note
    return {}


@app.get("/notes/{note_id}")
def get_note(note_id: int):
    # TODO: 404 when missing
    return {}


@app.delete("/notes/{note_id}")
def delete_note(note_id: int):
    # TODO: 404 when missing, 204 with an empty body when deleted
    return {}
