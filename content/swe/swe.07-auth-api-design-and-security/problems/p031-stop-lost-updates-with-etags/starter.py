import hashlib
import threading

from fastapi import FastAPI, Header, HTTPException, Response
from pydantic import BaseModel


class NoteIn(BaseModel):
    note: str


def build_app(seed):
    """Return a FastAPI app with GET and PUT /notes/{note_id}; seed is {note_id: text}."""
    app = FastAPI()
    # TODO: keep {"note": text, "version": 1} per note and add the two endpoints
    return app
