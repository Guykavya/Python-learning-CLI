import secrets
from urllib.parse import urlencode

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse

CLIENTS = {
    "printshop": {"redirect_uris": ["https://app.example.com/cb", "https://app.example.com/cb2"]},
    "mobile": {"redirect_uris": ["com.example.mobile:/oauth"]},
}


def build_app() -> FastAPI:
    app = FastAPI()

    @app.get("/authorize")
    def authorize(client_id: str, redirect_uri: str, state: str):
        client = CLIENTS.get(client_id)
        if client is None:
            raise HTTPException(400, "unknown client")
        # BUG: a "starts with" check accepts look-alike addresses
        if not any(redirect_uri.startswith(registered) for registered in client["redirect_uris"]):
            raise HTTPException(400, "redirect_uri is not registered for this client")
        code = secrets.token_urlsafe(24)
        return RedirectResponse(f"{redirect_uri}?{urlencode({'code': code, 'state': state})}", status_code=302)

    return app
