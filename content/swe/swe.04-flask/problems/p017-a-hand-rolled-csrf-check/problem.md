# A hand-rolled CSRF check

Chapter sections 9.2 and 9.3. A malicious page can make your browser send a `POST` to another site **with your cookies**. A CSRF token stops it: a secret value that the attacker's page cannot read. In `solution.py` write `create_app(test_config=None)` for a tiny bank (`SECRET_KEY` is set in the starter):

- `GET /form` shows an HTML form posting to `/deposit`, with a hidden input `csrf_token`.
- `POST /deposit` with form field `amount` (an integer) adds it to the balance and answers `Deposited <amount>`.
- `GET /balance` answers the balance as text. It must **never change data** (a GET that changes data cannot be protected by a token and can be triggered by an `<img>` tag).
- The balance lives in `app.extensions["bank"]["balance"]` (a dict in the starter).

The token:

1. It is created once per session (`secrets.token_urlsafe(32)`) and stored in `session["csrf_token"]`; it stays the same for the whole session and differs between sessions.
2. It is made available to templates as the function `csrf_token()` (a Jinja global), so the form can print it.
3. A `before_request` hook checks **every request that is not GET, HEAD or OPTIONS**: the token sent in the form field `csrf_token` (or the header `X-CSRF-Token`, for JavaScript) must equal the session's token. Missing, empty, wrong or non-ASCII (`é`) → **400**, and the view does not run.
4. Compare with **`hmac.compare_digest`** (a comparison whose time does not depend on where the strings differ), on **bytes**, because `compare_digest` raises `TypeError` for a `str` with non-ASCII characters.

## Example

```text
GET  /form                        -> HTML with <input type="hidden" name="csrf_token" value="Zk3...">
POST /deposit amount=50 csrf_token=Zk3...   -> 200 Deposited 50
POST /deposit amount=50                      -> 400, balance unchanged
```
