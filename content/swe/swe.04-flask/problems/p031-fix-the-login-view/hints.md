## Hint 1

For each bug ask: what does an attacker learn or gain? (1) Which names exist. (2) A session id they already know becomes a login. (3) Where the victim lands after logging in.

## Hint 2

(1) Look up the hash with `USERS.get(username, DUMMY_HASH)`, always call `check_password_hash`, and answer with one message. (2) One line before `session["user"] = ...`. (3) A function `safe_next(target)` that returns `target` only if it passes the checks of the statement, else `"/"`; `urllib.parse.urlsplit` gives `.scheme` and `.netloc`.

## Hint 3

```text
stored = USERS.get(username, DUMMY_HASH)
valid = check_password_hash(stored, password) and username in USERS
if not valid: return "Invalid username or password", 401
session.clear(); session["user"] = username
safe_next: reject empty, not starting with "/", starting with "//", containing "\", having a scheme or netloc
return redirect(safe_next(request.args.get("next")))
```
