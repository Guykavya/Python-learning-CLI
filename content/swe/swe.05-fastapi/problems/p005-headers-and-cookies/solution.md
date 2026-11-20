## Approach

Mark each parameter with where it comes from. The Python name decides the header or cookie name.

```python
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
```

Example: the header line `X-Token: t1` sent twice gives `x_token == ["t1", "t2"]`; with `str | None` you would get only one of them. A request carrying `Cookie: session=s123` gives `session == "s123"`.

The starter shows the trap: without `Header()` and `Cookie()`, FastAPI reads the four values from `?user_agent=...&session=...` in the URL, and the real headers are ignored.

## Complexity

O(number of headers) per request.

## Another way

Keep a different Python name and give the wire name yourself: `request_id: Annotated[str | None, Header(alias="X-Request-ID")] = None`. This is handy when the header name is not a valid identifier or is long. (`Header(convert_underscores=False)` instead keeps underscores on the wire; most proxies drop such headers, so avoid it.)
