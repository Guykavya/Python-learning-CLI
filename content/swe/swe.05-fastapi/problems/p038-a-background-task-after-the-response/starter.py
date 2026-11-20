import logging
from typing import Annotated

from fastapi import BackgroundTasks, Depends, FastAPI
from pydantic import BaseModel

logger = logging.getLogger("signup")


class Outbox:
    """The real mail sender would talk to an SMTP server; this one keeps a list."""

    def __init__(self):
        self.messages = []

    def send(self, to, subject, body):
        self.messages.append({"to": to, "subject": subject, "body": body})


OUTBOX = Outbox()


def get_outbox():
    return OUTBOX


class SignupIn(BaseModel):
    email: str


def send_welcome(outbox, email):
    # TODO: send the welcome message; catch and log any failure with logger.exception
    pass


app = FastAPI()


@app.post("/signup", status_code=201)
def signup(data: SignupIn, outbox: Annotated[Outbox, Depends(get_outbox)]):
    # TODO: add a BackgroundTasks parameter and schedule send_welcome(outbox, data.email)
    return {"email": data.email, "welcome": "queued"}
