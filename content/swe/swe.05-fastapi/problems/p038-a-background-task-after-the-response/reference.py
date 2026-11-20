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
    try:
        outbox.send(to=email, subject="Welcome to TaskFlow", body=f"Hi {email}, thanks for signing up.")
    except Exception:
        # The response is already gone: the log is the only place a failure can be seen.
        logger.exception("welcome email to %s failed", email)


app = FastAPI()


@app.post("/signup", status_code=201)
def signup(data: SignupIn, outbox: Annotated[Outbox, Depends(get_outbox)], background: BackgroundTasks):
    background.add_task(send_welcome, outbox, data.email)      # runs after the response is sent
    return {"email": data.email, "welcome": "queued"}
