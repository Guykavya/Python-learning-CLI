from typing import Annotated

from fastapi import Cookie, FastAPI, Header

app = FastAPI()


# TODO: these parameters have simple types and no Header()/Cookie(), so FastAPI reads
# them from the QUERY string. Tell FastAPI where each one really comes from.
@app.get("/whoami")
def whoami(
    user_agent: str | None = None,
    x_request_id: str | None = None,
    x_token: str | None = None,
    session: str | None = None,
):
    return {
        "user_agent": user_agent,
        "request_id": x_request_id,
        "tokens": [x_token] if x_token else [],
        "session": session,
        "logged_in": session is not None,
    }
