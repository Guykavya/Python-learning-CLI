## Approach

```python
def safe_next(target):
    if not target or not target.startswith("/") or target.startswith("//") or "\\" in target:
        return "/"
    parts = urlsplit(target)
    if parts.scheme or parts.netloc:
        return "/"
    return target


@app.route("/auth/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        stored = USERS.get(username, DUMMY_HASH)              # same work for unknown users
        valid = check_password_hash(stored, password) and username in USERS
        if not valid:
            return "Invalid username or password", 401
        session.clear()                                        # a new session for the new login
        session["user"] = username
        return redirect(safe_next(request.args.get("next")))
    return "login form"
```

Example: `next=https://evil.example/` does not start with `/`: refused. `next=//evil.example` starts with `/` but is a **scheme-relative URL** (browsers treat it as `https://evil.example`): refused by the `//` rule. `next=/\evil.example`: browsers turn the backslash into a slash, giving `//evil.example`: refused by the backslash rule. `next=/dashboard?tab=2` is a plain local path: accepted.

- **Bug 1.** Different answers (and different *speed*: an unknown name skips the slow hash) tell an attacker which accounts exist, and they can then target those. One answer, one amount of work. (A sign-up form still has to say "name taken"; protect it with rate limiting.)
- **Bug 2.** If an attacker can plant a session cookie in the victim's browser, then after the victim logs in the attacker's copy of that session is logged in too. A fresh session at login closes the door.
- **Bug 3.** A phishing link `https://yourapp/login?next=https://evil.example/` looks trustworthy and ends on a fake "please log in again" page.

## Complexity

One password hash check per attempt.

## Another way

Make `next` a **named endpoint** instead of a URL (`next=dashboard`, then `url_for(next)` if it is in an allow-list). No URL parsing is needed, so there is nothing to bypass.

## Not covered

Rate limiting and lockouts (section 16.8): they stop an attacker trying thousands of passwords.
