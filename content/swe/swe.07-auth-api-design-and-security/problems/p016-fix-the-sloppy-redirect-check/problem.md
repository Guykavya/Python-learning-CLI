# Fix the sloppy redirect check

Chapter section 5.2 (why each piece exists), section 5.3 (the tiny authorization server) and "Try it: the sloppy redirect check". After the user approves, the authorization server sends the browser back to the client's `redirect_uri` with the authorization **code**. If an attacker can choose where the code goes, the attacker gets the user's login.

`starter.py` is a small authorization server with one endpoint, `GET /authorize`. It decides if a `redirect_uri` is registered with `redirect_uri.startswith(registered)`. That lets look-alike addresses through:

```text
registered: https://app.example.com/cb
accepted:   https://app.example.com/cb/../x                 (a path trick)
accepted:   https://app.example.com/cbevil                  (more text after the registered one)
registered: https://app.example.com
accepted:   https://app.example.com.evil.net/cb             (a different host that starts the same)
```

Copy `starter.py` to `solution.py` and fix the check: a `redirect_uri` is accepted **only if the whole string is equal to one of the values registered for that client**. No prefix, no case folding, no trailing-slash tolerance, no parsing tricks.

Everything else stays as it is: a refused request answers **400** with **no** `Location` header and no code; an accepted one answers **302** to `redirect_uri?code=...&state=...`.

## Example

```text
GET /authorize?client_id=printshop&state=xyz&redirect_uri=https://app.example.com/cb
    -> 302 Location: https://app.example.com/cb?code=...&state=xyz
GET /authorize?client_id=printshop&state=xyz&redirect_uri=https://app.example.com.evil.net/cb
    -> 400
```
