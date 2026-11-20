# Headers and cookies

Chapter section 3.4 (and the table in 3.1). In `solution.py` define `app = FastAPI()` with one endpoint, `GET /whoami`, that reads:

| Python parameter | Comes from | Notes |
|---|---|---|
| `user_agent` | the header `User-Agent` | `str` or `None` |
| `x_request_id` | the header `X-Request-ID` | `str` or `None` |
| `x_token` | the header `X-Token`, which may be sent **several times** | a list of str, or `None` |
| `session` | the **cookie** `session` | `str` or `None` |

All four are optional: when the client does not send one, its value is `None`. Use `Annotated[..., Header()]` and `Annotated[..., Cookie()]`; FastAPI turns the underscores of the Python name into hyphens (`x_request_id` matches `X-Request-ID`), and header names are case-insensitive.

The endpoint returns

```python
{
    "user_agent": user_agent,
    "request_id": x_request_id,
    "tokens": x_token or [],
    "session": session,
    "logged_in": session is not None,
}
```

Note: `TestClient` sends `User-Agent: testclient` by itself, like a browser sends its own name. The tests remove that header when they need a request without it.

## Example

```text
GET /whoami
  User-Agent: demo/1.0
  X-Request-ID: abc-1
  X-Token: t1
  X-Token: t2
  Cookie: session=s123
-> {"user_agent": "demo/1.0", "request_id": "abc-1", "tokens": ["t1", "t2"],
    "session": "s123", "logged_in": true}

GET /whoami   (no headers, no cookie, no user agent)
-> {"user_agent": null, "request_id": null, "tokens": [], "session": null, "logged_in": false}
```
