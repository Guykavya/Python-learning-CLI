## Approach

```python
@app.get("/authorize")
def authorize(client_id: str, redirect_uri: str, state: str):
    client = CLIENTS.get(client_id)
    if client is None:
        raise HTTPException(400, "unknown client")
    if redirect_uri not in client["redirect_uris"]:        # the WHOLE string must match
        raise HTTPException(400, "redirect_uri is not registered for this client")
    code = secrets.token_urlsafe(24)
    return RedirectResponse(f"{redirect_uri}?{urlencode({'code': code, 'state': state})}", status_code=302)
```

`in` on a list uses `==`, so only an identical string passes. Every trick of the test list fails for a simple reason: the string is different. Parsing the URL and comparing the host would be worse: URL parsers disagree with browsers on `@`, `\`, `..` and case, and every disagreement is a hole. A refused request must not redirect at all: redirecting an error to an unverified address is itself an open redirect (chapter 5.3).

## Complexity

O(number of registered URIs x length), tiny.

## Another way

Store the registered URIs in a `set` for O(1) lookup. The chapter's demo does this (`redirect_uri not in client["redirect_uris"]` with a set). PKCE (section 5.2) limits the damage of a stolen code, but it is a second layer, not a replacement for this check.
