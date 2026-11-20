# Tests that catch the bugs

Chapter section 21. A test that cannot fail is worth nothing. Here **you** write the tests, and the grader tests *your tests*: it runs them against a correct app (they must **pass**) and against **four deliberately broken** apps (each broken app must make the matching check **fail**, with an `AssertionError`).

The app under test (its code is in `test_solution.py`; read it) has these routes. Forms are sent as normal form data:

| Route | Behaviour |
|---|---|
| `GET /csrf` | plain text: the CSRF token of the current session (created on first use) |
| `POST /login` | fields `username`, `password`, `csrf_token`. Users: `asha` / `pw-asha`, `ravi` / `pw-ravi`. Success `200 ok`; wrong login `401`. **A successful login clears the session**, so the old CSRF token is gone: ask `/csrf` again afterwards. |
| `POST /posts` | fields `title`, `csrf_token`; needs login (**401** otherwise); answers **201** with `{"id": ...}` |
| `POST /posts/<id>/delete` | field `csrf_token`; needs login (401); **404** if missing; **403** unless you are the author; **204** on success |
| every `POST` | **400** unless `csrf_token` equals the token of the session |

In `solution.py` write three plain functions. Each receives `make_client`, a function with no arguments that returns **a new test client of the same app** (call it twice to get two different "browsers"). Use plain `assert` statements with messages; **do not catch** the assertion errors.

- `check_login(make_client)`: a correct login works and the session then lets you create a post; a wrong password gives **401** and does **not** log you in.
- `check_csrf(make_client)`: a logged-in user's `POST /posts` is refused with **400** when the token is **missing** and when it is **wrong**, and accepted with the right token.
- `check_owner_only(make_client)`: Asha creates a post; Ravi cannot delete it (**403**) and Asha still can (**204**).

The four broken apps: `csrf_not_checked` (no token needed), `csrf_value_ignored` (any non-empty token is accepted), `no_owner_check` (anybody may delete), `any_password` (any password works for an existing user). **`check_csrf` must catch both CSRF bugs**, which is the interesting part: a test that only sends a missing token lets the second bug through.

## Example

```python
def check_csrf(make_client):
    client = make_client()
    ...  # log in, then POST /posts with no token and assert 400, with "wrong" and assert 400, with the real token and assert 201
```
