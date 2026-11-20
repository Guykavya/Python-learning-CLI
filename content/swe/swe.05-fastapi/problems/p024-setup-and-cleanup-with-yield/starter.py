from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()
SAVED = []          # what has been committed


class ListSession:
    """A stand-in for a database session: added items are pending until commit."""

    def __init__(self):
        self.pending = []

    def add(self, item):
        self.pending.append(item)

    def commit(self):
        SAVED.extend(self.pending)
        self.pending = []

    def rollback(self):
        self.pending = []

    def close(self):
        self.pending = []


def get_session_factory():
    return ListSession


def get_session(factory: Annotated[type, Depends(get_session_factory)]):
    # TODO: open one session, yield it, commit on success,
    #       roll back and re-raise on an exception, always close.
    yield factory()


Session = Annotated[ListSession, Depends(get_session)]


class NoteIn(BaseModel):
    text: str


@app.post("/notes", status_code=201)
def create_note(data: NoteIn, session: Session):
    session.add(data.text)
    return {"text": data.text}


@app.post("/notes/duplicate", status_code=201)
def create_duplicate(data: NoteIn, session: Session):
    session.add(data.text)
    raise HTTPException(409, "Note already exists")


@app.post("/notes/crash", status_code=201)
def create_with_bug(data: NoteIn, session: Session):
    session.add(data.text)
    raise RuntimeError("bug in the endpoint")
