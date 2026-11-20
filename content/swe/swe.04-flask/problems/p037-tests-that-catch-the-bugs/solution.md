## Approach

Each check states one rule of the app and asserts both sides of it: what must be **allowed** and what must be **refused**. A test that checks only the happy path passes on every broken app.

```python
def token(client):
    return client.get("/csrf").get_data(as_text=True)


def log_in(client, username, password):
    return client.post("/login", data={"username": username, "password": password, "csrf_token": token(client)})


def check_csrf(make_client):
    client = make_client()
    assert log_in(client, "asha", "pw-asha").status_code == 200
    assert create_post(client, csrf=False).status_code == 400, "a POST without a CSRF token must be refused (400)"
    assert create_post(client, csrf="wrong-token").status_code == 400, "a POST with a WRONG CSRF token must be refused (400)"
    assert create_post(client).status_code == 201, "a POST with the right token must work"
```

(Full file: `reference.py`.)

What each broken app teaches:

| Broken app | Which assertion catches it | The lesson |
|---|---|---|
| `csrf_not_checked` | the "missing token → 400" line | test the refusal, not only the success |
| `csrf_value_ignored` | the "wrong token → 400" line | a check that only tests `token is present` is half a test |
| `no_owner_check` | Ravi's delete must be 403 | a second user is needed to test authorisation |
| `any_password` | the wrong password must be 401 | test the failing login, and that it did not log in |

Two traps in the *tests themselves*: the login clears the session (so the CSRF token must be fetched again after it), and the "Asha can still delete" assertion at the end stops a check that passes only because *everything* is forbidden.

This is **mutation testing** by hand: break the code on purpose and see whether the tests notice. Tools such as `mutmut` do it automatically.

## Complexity

Each check makes a handful of requests; the whole file runs in about a second.

## Another way

Parametrised pytest tests and fixtures (`client`, `login`) would hold the same assertions; the grader here wants plain functions so that it can run them against several apps.

## Not covered

Property-based tests (`hypothesis`) that invent the inputs for you.
