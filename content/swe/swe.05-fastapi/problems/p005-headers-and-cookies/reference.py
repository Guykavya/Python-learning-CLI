from typing import Annotated

from fastapi import Cookie, FastAPI, Header

app = FastAPI()


@app.get("/whoami")
def whoami(
    user_agent: Annotated[str | None, Header()] = None,
    x_request_id: Annotated[str | None, Header()] = None,
    x_token: Annotated[list[str] | None, Header()] = None,
    session: Annotated[str | None, Cookie()] = None,
):
    return {
        "user_agent": user_agent,
        "request_id": x_request_id,
        "tokens": x_token or [],
        "session": session,
        "logged_in": session is not None,
    }
