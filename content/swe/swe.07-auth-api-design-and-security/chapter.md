# Chapter 7 (SWE): Auth, API design and security

In the last three chapters you built web apps with Flask, FastAPI and Django. Each chapter had a small security section: hash passwords, sign tokens, check that the user owns the object. This chapter turns those sections into a full discipline. Security is not a feature you add at the end. It is a way of asking, for every line that touches a request, **"what if the person on the other side is not who I hope they are?"**

You will learn the parts in the order an attacker meets them: how users prove who they are (passwords, sessions, tokens, OAuth2, API keys), what they are allowed to do (roles, ownership, scopes), how the API should look so that it is hard to misuse (REST design, pagination, filtering, versioning), how to survive abuse (rate limiting, idempotency), and how to keep bad input and leaked secrets from becoming a breach (validation, the OWASP Top 10, secrets management). Section 16 maps the OWASP Top 10 to Python code, and the last section is a real security audit: a deliberately vulnerable API that you attack, fix and test.

By the end you reach two outcomes, and both are tested, not just discussed:

- You can **prevent a user from reading another user's data, and write a test that proves it** (section 8). This is the most common serious bug in real APIs.
- You can **make a payment-style endpoint safe to call twice**, so a retry never charges a customer two times (section 13).

Prerequisites: swe.02 (HTTP, status codes), swe.03 (SQL), and swe.04 or swe.05 (a web framework; we use FastAPI because its `TestClient` runs everything in one process, but every idea applies to Flask and Django too). The basics of hashing and JWT from swe.04 section 15 and swe.05 section 12 are referenced, then taken further.

> **Offline and ethical rules for this chapter.** Every example runs on your own computer with the standard library, FastAPI's `TestClient`, SQLite and PyJWT. Nothing touches the internet. Packages that are not installed in this course environment (Argon2, bcrypt, `cryptography`, Redis, a real OAuth2 provider) are described in clearly marked **Try it on your machine** steps, with exact commands and no invented output. The attacks shown run only against small toy apps inside this chapter. Attacking a system you do not own, or have no written permission to test, is illegal in most countries. Learn the attacks so you can defend against them.

Every output block in this chapter was produced by actually running the code above it, with these versions (patch versions may differ; the behaviour described is stable):

```bash run
python -c "
import sys, fastapi, starlette, pydantic, jwt, httpx, sqlite3
print('python   ', sys.version.split()[0])
for m in (fastapi, starlette, pydantic, jwt, httpx):
    print(f'{m.__name__:9}', m.__version__)
print('sqlite   ', sqlite3.sqlite_version)
"
```
```text
python    3.14.4
fastapi   0.162.0
starlette 1.10.0
pydantic  2.14.3
jwt       2.15.1
httpx     0.28.1
sqlite    3.46.1
```

The running example is the **Pagebound Orders API**: users place orders and pay for them. Small pieces appear in each section, and section 17 gathers them into one app to audit.

## Table of contents

1. [Thinking like an attacker](#1-thinking-like-an-attacker)
2. [Passwords done properly](#2-passwords-done-properly)
3. [Sessions and cookies](#3-sessions-and-cookies)
4. [Tokens and JWT, beyond the basics](#4-tokens-and-jwt-beyond-the-basics)
5. [OAuth2 and OpenID Connect](#5-oauth2-and-openid-connect)
6. [API keys, one-time codes and signed webhooks](#6-api-keys-one-time-codes-and-signed-webhooks)
7. [Authorisation: roles, ownership and policies](#7-authorisation-roles-ownership-and-policies)
8. [Object-level authorisation: stopping IDOR, and testing it](#8-object-level-authorisation-stopping-idor-and-testing-it)
9. [REST API design that is hard to misuse](#9-rest-api-design-that-is-hard-to-misuse)
10. [Pagination, filtering and sorting](#10-pagination-filtering-and-sorting)
11. [Rate limiting and abuse protection](#11-rate-limiting-and-abuse-protection)
12. [Evolving an API: versions, deprecation and concurrent edits](#12-evolving-an-api-versions-deprecation-and-concurrent-edits)
13. [Idempotency keys: a payment endpoint that is safe to call twice](#13-idempotency-keys-a-payment-endpoint-that-is-safe-to-call-twice)
14. [Input validation, injection and other unsafe operations](#14-input-validation-injection-and-other-unsafe-operations)
15. [Secrets, logging, errors and dependencies](#15-secrets-logging-errors-and-dependencies)
16. [The OWASP Top 10, read as a Python developer](#16-the-owasp-top-10-read-as-a-python-developer)
17. [Project: security audit and hardening of an API](#17-project-security-audit-and-hardening-of-an-api)
18. [Common traps](#18-common-traps)
19. [Collected traps](#19-collected-traps)
20. [Summary](#20-summary)

## 1. Thinking like an attacker

### 1.1 What are we protecting, and from whom?

Before any code, answer two questions about the system:

- **Assets:** what is valuable? In the Pagebound API: customer personal data, order history, payment records, account access, the money itself, and the service being available.
- **Attackers:** who might misuse it, and what can they already do? A curious *logged-in user* who edits an id in a URL. A *bot* that tries a million stolen passwords. A *competitor* scraping prices. A *former employee* whose key still works. A *stranger* who found your `.env` file on GitHub. Each has different tools, so each needs different defences.

An attacker does not need genius. Most real breaches are the same few mistakes: an endpoint that forgot to check ownership, a password stored badly, a secret committed to git, an input that was trusted.

### 1.2 Words you must use exactly

| Word | Meaning | Example |
|---|---|---|
| **Authentication** (authn) | proving who you are | password, token, key |
| **Authorisation** (authz) | deciding what you may do | "only the owner may cancel this order" |
| **Validation** | checking that input has the right shape | "quantity is an integer from 1 to 99" |
| **Confidentiality** | only the right people can read | another user cannot read my orders |
| **Integrity** | data cannot be changed secretly | a token or amount cannot be tampered with |
| **Availability** | the service keeps working | one client cannot take it down |
| **Vulnerability** | a weakness in the system | a missing ownership check |
| **Exploit** | a way to use a vulnerability | requesting `/orders/2` as user 1 |
| **Risk** | how likely and how bad | likely and exposes every customer: high |

Three principles carry most of the weight:

1. **Deny by default.** Access is refused unless a rule allows it. A new endpoint that forgets its check should fail *closed* (nobody gets in), not *open*.
2. **Least privilege.** Every user, service and key gets only the permissions it needs. A report job should not have the power to delete users.
3. **Defence in depth.** Never rely on a single layer. Validate input, check ownership in the query, use a database constraint and keep logs. If one layer has a hole, another catches it.

And one rule that explains most bugs: **everything that arrives over the network is untrusted.** That includes the body, the query string, the headers, cookies, file names, the `id` in the path, a field the client "should not" send, and a token the client "cannot" change.

### 1.3 A small threat model: STRIDE

**STRIDE** is a checklist of six kinds of threat. For each part of your system you ask "could this happen here?" The table maps each threat to the sections of this chapter that defend against it:

| Threat | Question | Defence | Section |
|---|---|---|---|
| **S**poofing | can someone pretend to be another user? | passwords, sessions, tokens, OAuth2, API keys | 2 to 6 |
| **T**ampering | can data or a token be changed in transit or storage? | signatures, validation, constraints | 4, 6, 14 |
| **R**epudiation | can a user deny what they did? | audit logs | 15 |
| **I**nformation disclosure | can someone read what they should not? | authorisation, ownership, error messages | 7, 8, 15 |
| **D**enial of service | can one client make the service unusable? | rate limits, size limits | 11 |
| **E**levation of privilege | can a normal user act as an admin? | role checks, mass-assignment protection | 7, 8 |

### 1.4 Six questions for every endpoint

You will use this checklist for the rest of the chapter, and in the final audit. For **each endpoint**, ask:

1. **Who is calling?** Is there authentication, and is it required?
2. **May they do this to this object?** Authorisation, including *ownership*.
3. **Is every input checked?** Types, ranges, sizes, allowed values, and unexpected extra fields.
4. **What can this cost?** Rate limit, page size limit, request size, work per call.
5. **What if it is called twice?** Safe to retry? Idempotent where money or stock is involved?
6. **What do we log, and what do we leak?** Audit trail yes, passwords and tokens never; error messages that help users, not attackers.

### 1.5 What HTTPS does and does not do

**TLS** (the "S" in HTTPS) encrypts traffic between the browser and the server and proves the server's identity. It stops someone on the café Wi-Fi from reading passwords and cookies. It does **not** stop a logged-in user from requesting someone else's order, does not validate input and does not protect a leaked database. It ends at your reverse proxy or load balancer, so inside your network traffic may be plain HTTP; framework settings such as "trust the proxy's `X-Forwarded-Proto` header" decide whether your app thinks a request was secure (swe.06 section 17). Treat HTTPS as the *entry fee* for security, never as the whole of it.

### Try it: name the threat

Classify each bug with one STRIDE letter: (a) a JWT with no signature check lets anyone claim to be user 1; (b) the 500 error page prints the SQL query and the database password; (c) a script sends 10,000 login requests per second; (d) there is no log of who refunded an order.

<details><summary>Answer</summary>

(a) **S**poofing (and Elevation of privilege). (b) **I**nformation disclosure. (c) **D**enial of service (and a brute-force attack on authentication). (d) **R**epudiation: nobody can prove who did it. Many bugs fit more than one letter; the point of STRIDE is to make you ask all six questions, not to label perfectly.

</details>

## 2. Passwords done properly

### 2.1 The attacker's view

A stolen database is the common disaster. If passwords are stored in plain text, every account (and every account on other sites where users reused the password) is lost at once. If they are stored with a fast hash such as SHA-256, a graphics card can test billions of guesses per second, so most real passwords fall in hours. The defence is a **slow, salted, memory-hard hash**:

- **Salt:** a random value per user, stored next to the hash. Two users with the same password get different hashes, and precomputed "rainbow tables" are useless.
- **Slow and memory-hungry:** the hash is designed to cost, say, 50 milliseconds and 16 MiB of memory *per guess*. A login costs you almost nothing, but a billion guesses costs the attacker years.
- **Parameters stored with the hash:** so you can raise the cost later without breaking old passwords.

You met `hashlib.scrypt` in swe.04 and swe.05. Here is a complete password module that adds what real systems need: parameters inside the stored string, a check for outdated hashes, and an upgrade path.

### 2.2 A password module

```python
# passwords.py
import base64
import hashlib
import hmac
import os

N, R, P = 2**14, 8, 1            # the current cost: 16 MiB of memory, about 50 ms (machine-specific)


def _derive(password: str, salt: bytes, n: int, r: int, p: int) -> bytes:
    # scrypt needs about 128*n*r bytes; maxmem must be larger than that or hashlib raises ValueError
    return hashlib.scrypt(password.encode(), salt=salt, n=n, r=r, p=p, maxmem=256 * n * r)


def hash_password(password: str, *, n: int = N, r: int = R, p: int = P) -> str:
    salt = os.urandom(16)
    digest = _derive(password, salt, n, r, p)
    return "$".join(["scrypt", str(n), str(r), str(p),
                     base64.b64encode(salt).decode(), base64.b64encode(digest).decode()])


def verify_password(password: str, stored: str) -> bool:
    try:
        scheme, n, r, p, salt_b64, digest_b64 = stored.split("$")
        if scheme != "scrypt":
            return False
        expected = base64.b64decode(digest_b64)
        actual = _derive(password, base64.b64decode(salt_b64), int(n), int(r), int(p))
    except (ValueError, TypeError):
        return False
    return hmac.compare_digest(actual, expected)         # constant-time comparison


def needs_rehash(stored: str) -> bool:
    """True if this hash was made with weaker parameters than the current ones."""
    try:
        _, n, r, p, *_ = stored.split("$")
        return (int(n), int(r), int(p)) != (N, R, P)
    except ValueError:
        return True


def verify_and_upgrade(password: str, stored: str):
    """Return (ok, new_hash_or_None). Call it at login: the password is in memory only now."""
    if not verify_password(password, stored):
        return False, None
    return True, (hash_password(password) if needs_rehash(stored) else None)
```

```python run
from passwords import hash_password, needs_rehash, verify_and_upgrade, verify_password

h = hash_password("correct horse battery")
print(h.split("$")[:4], "... salt and digest follow")
print(verify_password("correct horse battery", h), verify_password("wrong", h), verify_password("x", "garbage"))
print("two hashes of one password differ:", hash_password("same") != hash_password("same"))

# an old account, hashed years ago when 2**12 was considered enough
legacy = hash_password("old-password", n=2**12)
print("legacy needs rehash:", needs_rehash(legacy), "| current:", needs_rehash(h))
ok, new = verify_and_upgrade("old-password", legacy)
print("login ok:", ok, "| upgraded to:", new.split("$")[1:4])
print("wrong password never upgrades:", verify_and_upgrade("nope", legacy))
```
```text
['scrypt', '16384', '8', '1'] ... salt and digest follow
True False False
two hashes of one password differ: True
legacy needs rehash: True | current: False
login ok: True | upgraded to: ['16384', '8', '1']
wrong password never upgrades: (False, None)
```

Study the design:

- The stored string is **self-describing** (`scrypt$16384$8$1$salt$hash`). Raise `N` next year and old hashes still verify, because `verify_password` reads the parameters from the string.
- **`verify_and_upgrade`** is the trick for upgrading without asking users to reset anything: at a successful login you have the plain password in memory for one moment, so you can re-hash it with the new parameters and save it. Users who never log in keep the old hash, which is no worse than before.
- **`hmac.compare_digest`** compares in constant time. A normal `==` returns as soon as it finds a different byte, so an attacker timing many requests could learn the right hash byte by byte.
- **`maxmem`:** scrypt needs about `128 * n * r` bytes. Python's default limit is 32 MiB, so `n=2**15` fails without the argument. Try it:

```python run
import hashlib

try:
    hashlib.scrypt(b"pw", salt=b"0123456789abcdef", n=2**15, r=8, p=1)
except ValueError as exc:
    print("default maxmem:", exc)
key = hashlib.scrypt(b"pw", salt=b"0123456789abcdef", n=2**15, r=8, p=1, maxmem=2**27)
print("with maxmem set:", len(key), "bytes")
```
```text
default maxmem: [digital envelope routines] memory limit exceeded
with maxmem set: 64 bytes
```

> **Do not invent your own scheme.** The module above shows the *ideas*. In a real project use a maintained library or your framework's built-in (Django's `make_password`, Werkzeug's `generate_password_hash`, Passlib or `argon2-cffi`). They already handle the edge cases.

> **Try it on your machine**: Argon2id is the algorithm current guidance recommends first (the winner of the Password Hashing Competition), then scrypt or bcrypt.
>
> ```bash
> pip install argon2-cffi
> python -c "from argon2 import PasswordHasher; h = PasswordHasher(); x = h.hash('pw'); print(x[:30]); print(h.verify(x, 'pw')); print(h.check_needs_rehash(x))"
> ```
>
> Expected: a string beginning with `$argon2id$v=19$m=` followed by the library's default cost numbers, then `True`, then `False`. The library gives you `check_needs_rehash`, the same idea as our `needs_rehash`.

### 2.3 A pepper (optional extra layer)

A **pepper** is a secret that is *not* stored in the database: it lives in the environment or a secrets manager. You mix it into the password before hashing, for example with `HMAC-SHA256(pepper, password)`. If an attacker steals only the database, they also need the pepper to test guesses. The cost: you can never lose or rotate the pepper casually, because every hash depends on it, so keep a version number next to the hash. Peppers are a useful extra, but salt plus a slow hash is the foundation.

### 2.4 Password policy: what current guidance says

Old rules ("one capital, one digit, one symbol, change every 90 days") made people choose `Password1!`. Current guidance (NIST SP 800-63B, written from memory here; check the latest text) prefers:

- A **minimum length** (at least 8, ideally 12 or more) and **allow long passwords and passphrases**, with spaces.
- **No forced composition rules** and **no forced periodic change** (change only after a suspected breach).
- **Reject known-bad passwords**: a list of common passwords and passwords seen in breaches (the "Have I Been Pwned" range API can be queried safely with only the first five characters of the hash).
- A **maximum length** (say 128 to 1,024 characters) so that a client cannot send a 100 MB "password" and make your server hash it (a denial of service).

```python run
COMMON = {"password", "123456", "qwerty", "letmein", "iloveyou", "password1"}

def check_password_policy(password: str, username: str = "") -> list[str]:
    problems = []
    if len(password) < 10:
        problems.append("use at least 10 characters")
    if len(password) > 256:
        problems.append("use at most 256 characters")
    if password.lower() in COMMON:
        problems.append("this password is too common")
    if username and username.lower() in password.lower():
        problems.append("do not include your username")
    return problems

for pw in ["short", "password", "ada-lovelace-rules", "correct horse battery staple", "x" * 300]:
    print(f"{pw[:28]!r:32}", check_password_policy(pw, "ada") or "ok")
```
```text
'short'                          ['use at least 10 characters']
'password'                       ['use at least 10 characters', 'this password is too common']
'ada-lovelace-rules'             ['do not include your username']
'correct horse battery staple'   ok
'xxxxxxxxxxxxxxxxxxxxxxxxxxxx'   ['use at most 256 characters']
```

Two comments. The policy tells the user *why*, so they can fix it. And the message about the username is useful here; an error that reveals secrets about *other* accounts never is (next section).

### 2.5 The login endpoint: do not leak who has an account

Two innocent-looking behaviours give attackers information:

- Answering "no such user" for a wrong username but "wrong password" for a wrong password tells an attacker which e-mails are registered (**user enumeration**), the first step of targeted phishing and credential stuffing.
- If an unknown user is rejected instantly but a known user takes 50 ms (the time to hash), the *timing* gives the same information.

The fix: always return one generic message, and **always do one hash verification**, even when the user does not exist, by verifying against a dummy hash. A test can check this deterministically, without measuring time, by counting calls:

```python run
from unittest import mock

import passwords

DUMMY_HASH = passwords.hash_password("dummy-password-for-timing")      # made once, at start-up
USERS = {"ada": passwords.hash_password("ada-secret-pass")}


def login(username: str, password: str) -> str:
    stored = USERS.get(username, DUMMY_HASH)
    ok = passwords.verify_password(password, stored)
    if username in USERS and ok:
        return "welcome"
    return "invalid username or password"            # one message for every failure

calls = []
real = passwords.verify_password
with mock.patch.object(passwords, "verify_password", side_effect=lambda *a: calls.append(a) or real(*a)):
    print(login("ada", "ada-secret-pass"))
    print(login("ada", "wrong"))
    print(login("nobody", "anything"))
print("hash verifications run:", len(calls), "(one per attempt, even for the unknown user)")
```
```text
welcome
invalid username or password
invalid username or password
hash verifications run: 3 (one per attempt, even for the unknown user)
```

The same care applies to **"forgot password"** (always answer "if that address exists, we sent an e-mail") and to **registration** (use e-mail confirmation instead of announcing "this address is taken", where you can).

Lastly, **throttle logins** (section 11). Slow hashing makes each guess costly for the attacker, but a rate limit stops millions of guesses across stolen-password lists ("credential stuffing"). Add multi-factor authentication (TOTP, passkeys) for sensitive accounts; it is the strongest single defence against stolen passwords, and is described in section 6.

### 2.6 Reset tokens

A password-reset link carries a **one-time secret** that proves control of the e-mail address. The rules:

- Generate it with `secrets.token_urlsafe(32)`, never `random`.
- Store only a **hash** of it (`sha256`), as you would a password; a stolen database then does not hand out working reset links. A fast hash is fine here because the token has 256 bits of randomness, so there is nothing to guess.
- Give it a **short life** (15 to 60 minutes), make it **single-use**, and invalidate it when the password changes.

```python run
import hashlib
import secrets

class ResetTokens:
    def __init__(self, now):
        self.now, self.rows = now, {}

    def create(self, user_id: int, ttl: int = 900) -> str:
        token = secrets.token_urlsafe(32)
        self.rows[hashlib.sha256(token.encode()).hexdigest()] = (user_id, self.now() + ttl)
        return token

    def consume(self, token: str):
        key = hashlib.sha256(token.encode()).hexdigest()
        row = self.rows.pop(key, None)                       # pop: single use
        if row is None or row[1] < self.now():
            return None
        return row[0]

clock = [1000.0]
tokens = ResetTokens(now=lambda: clock[0])
t = tokens.create(user_id=7)
print("token length:", len(t), "| stored as hash:", t not in tokens.rows)
print("first use  :", tokens.consume(t))
print("second use :", tokens.consume(t))
t2 = tokens.create(7)
clock[0] += 901
print("after 15 min:", tokens.consume(t2))
```
```text
token length: 43 | stored as hash: True
first use  : 7
second use : None
after 15 min: None
```

The `now` function is passed in, so the test moves a fake clock instead of sleeping. You will see this pattern again in rate limiting.

### Try it: the cost upgrade

Your site uses scrypt `N = 2**14`. You decide to move to `N = 2**15`. Which accounts have the new cost after one week, and how do you upgrade the accounts of people who never come back?

<details><summary>Answer</summary>

Only accounts whose owners logged in during the week: `verify_and_upgrade` re-hashes on successful login. Dormant accounts keep the old hash. You cannot re-hash without the plain password. Options: accept it (the old hash is still decent), or wrap the old hash in the new one (`scrypt_new(old_hash)`) in a one-off migration, then unwrap-and-upgrade at next login. Never "upgrade" by weakening anything.

</details>

### Try it: why not just encrypt passwords?

A colleague says "encrypt the passwords with AES instead, so we can send users their password when they forget it". What is wrong with the plan?

<details><summary>Answer</summary>

Encryption is reversible, so anyone who gets the key (or the application server, where the key must live) reads **all** passwords. A hash is one-way: the server never knows the password after login, so it cannot be stolen from the server and cannot be e-mailed (which is also a bad idea). Forgotten passwords are handled by a reset token (2.6), never by recovery.

</details>

## 3. Sessions and cookies

### 3.1 What a session is

HTTP forgets you after every request. A **session** is the server's way of remembering that this browser logged in. After a successful login, the server creates a random **session id**, stores `session id -> user` on the server, and sends the id to the browser in a **cookie**. The browser returns the cookie with every request, and the server looks the id up.

| | Server-side session | Signed-cookie session (Flask default) | JWT in a header (section 4) |
|---|---|---|---|
| What the client holds | a random id | the whole session data, signed | a signed token |
| Server stores | a table of sessions | nothing | nothing (or a deny-list) |
| Logout / revoke now | delete the row: instant | hard: the cookie stays valid until it expires | hard, same reason |
| Size limits | none | about 4 KB (cookie limit) | header size |
| Good for | browser web apps | small, low-risk state | APIs and mobile apps, many services |

For a browser-based site, **server-side sessions with an `HttpOnly` cookie are the safest, simplest choice**. They can be revoked at once, and the cookie holds nothing useful if it is read.

### 3.2 A server-side session store

```python run
import hashlib
import secrets

from fastapi import Cookie, FastAPI, HTTPException, Response
from fastapi.testclient import TestClient


class SessionStore:
    def __init__(self, now, ttl=3600):
        self.now, self.ttl, self.rows = now, ttl, {}

    @staticmethod
    def _key(session_id: str) -> str:
        return hashlib.sha256(session_id.encode()).hexdigest()       # a leaked table cannot be used as cookies

    def create(self, user: str) -> str:
        session_id = secrets.token_urlsafe(32)                       # 256 random bits
        self.rows[self._key(session_id)] = {"user": user, "expires": self.now() + self.ttl}
        return session_id

    def get(self, session_id: str | None):
        row = self.rows.get(self._key(session_id)) if session_id else None
        if row is None or row["expires"] < self.now():
            return None
        return row["user"]

    def destroy(self, session_id: str | None):
        if session_id:
            self.rows.pop(self._key(session_id), None)


clock = [0.0]
store = SessionStore(now=lambda: clock[0])
app = FastAPI()


@app.post("/login")
def login(username: str, password: str, response: Response):
    if password != "right":                                           # stand-in for verify_password
        raise HTTPException(401, "invalid username or password")
    response.set_cookie("sid", store.create(username), httponly=True, secure=True,
                        samesite="lax", max_age=3600, path="/")
    return {"ok": True}


@app.get("/me")
def me(sid: str | None = Cookie(default=None)):
    user = store.get(sid)
    if user is None:
        raise HTTPException(401, "not logged in")
    return {"user": user}


@app.post("/logout")
def logout(response: Response, sid: str | None = Cookie(default=None)):
    store.destroy(sid)
    response.delete_cookie("sid", path="/")
    return {"ok": True}


client = TestClient(app, base_url="https://testserver")      # https, so Secure cookies are sent back
r = client.post("/login", params={"username": "ada", "password": "right"})
print(r.status_code, "| Set-Cookie flags:", sorted(p.strip().split("=")[0] for p in r.headers["set-cookie"].split(";")[1:]))
print("me     :", client.get("/me").json())
clock[0] += 3601
print("1h later:", client.get("/me").status_code)
client.post("/login", params={"username": "ada", "password": "right"})
client.post("/logout")
print("after logout:", client.get("/me").status_code)
```
```text
200 | Set-Cookie flags: ['HttpOnly', 'Max-Age', 'Path', 'SameSite', 'Secure']
me     : {'user': 'ada'}
1h later: 401
after logout: 401
```

(In a real app the password goes in the request **body**, never the query string, because URLs end up in logs and browser history. The query form here only keeps the example short.)

The cookie flags are the security settings of the session:

| Flag | Effect | Why |
|---|---|---|
| `HttpOnly` | JavaScript cannot read the cookie | an XSS bug cannot steal the session |
| `Secure` | sent only over HTTPS | no leaking over plain HTTP |
| `SameSite=Lax` (or `Strict`) | not sent on cross-site POSTs/subrequests | blocks most CSRF (below) |
| `Max-Age` / `Expires` | lifetime | limits the damage of a stolen cookie |
| `Path`, `Domain` | which URLs get it | keep it narrow; omit `Domain` unless you need sub-domains |

The prefix `__Host-` on the cookie name (`__Host-sid`) makes modern browsers insist on `Secure`, `Path=/` and no `Domain`, so another sub-domain cannot overwrite your cookie.

### 3.3 Session fixation

In a **session fixation** attack the attacker obtains a valid session id (by visiting the site), plants it in the victim's browser (through a link or a sub-domain cookie), waits for the victim to log in, and then uses the same id, which now belongs to a logged-in user. The vulnerable code keeps the id it already had when the user logs in. The fix is one rule: **create a new session id at login** (and at any privilege change), and throw the old one away.

```python run
import secrets

class Sessions:
    def __init__(self):
        self.rows = {}

    def anonymous(self):
        sid = secrets.token_urlsafe(16)
        self.rows[sid] = {"user": None}
        return sid

    def login_vulnerable(self, sid, user):
        self.rows[sid]["user"] = user                  # BUG: keeps the id the attacker knows
        return sid

    def login_safe(self, sid, user):
        self.rows.pop(sid, None)                       # drop the old id
        new = secrets.token_urlsafe(16)
        self.rows[new] = {"user": user}
        return new

s = Sessions()
planted = s.anonymous()                                # attacker visits the site and learns this id
victim_sid = s.login_vulnerable(planted, "victim")     # victim logs in with the planted id
print("vulnerable: attacker's id now means:", s.rows[planted]["user"])

s = Sessions()
planted = s.anonymous()
victim_sid = s.login_safe(planted, "victim")
print("safe      : attacker's id now means:", s.rows.get(planted), "| victim got a new id:", victim_sid != planted)
```
```text
vulnerable: attacker's id now means: victim
safe      : attacker's id now means: None | victim got a new id: True
```

### 3.4 Logout and timeouts

- **Logout must destroy the server-side session**, not only delete the cookie in the browser (a copied cookie would still work). The example above did this.
- Use **two timeouts**: an *idle* timeout (expire after 30 minutes of inactivity) and an *absolute* timeout (expire after, say, 12 hours however active). Shorter for banks, longer for low-risk sites.
- Offer **"log out everywhere"** by deleting all of a user's session rows. With signed-cookie sessions or JWTs this needs extra work, which is the real cost of those designs.
- Delete a user's sessions when their **password changes** or the account is disabled.

### 3.5 CSRF: the browser sends your cookie for you

**Cross-Site Request Forgery**: you are logged in to `shop.example`. You open a malicious page that contains a hidden form posting to `https://shop.example/orders/42/cancel`. Your browser attaches your session cookie, because the request goes to `shop.example`. The server sees a valid session and cancels the order. The attacker never saw the cookie and never needed it.

Defences, from strongest to weakest, and usually combined:

1. **`SameSite=Lax` or `Strict` cookies.** Modern browsers then do not attach the cookie on cross-site POST requests. Lax is the default in current browsers, but set it explicitly.
2. **A CSRF token**: a random value tied to the session, put in each form (`<input type="hidden">`) or a header, and checked on every state-changing request. A foreign site cannot read it, so it cannot include it. (Django, swe.06 section 11.3, and Flask-WTF do this for you.)
3. **Check the `Origin` (or `Referer`) header** of unsafe requests against your own site.
4. **Never change state on `GET`.** A `GET` link or `<img>` tag is trivially sent cross-site.

APIs that authenticate with an `Authorization: Bearer ...` header are not vulnerable in this way, because the browser does not add that header by itself. That is one reason token APIs and cookie sessions need different protection. Here is an `Origin` check as a reusable dependency, with a test that forges the origin:

```python run
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.testclient import TestClient

ALLOWED_ORIGINS = {"https://shop.example"}


def same_site_only(request: Request):
    if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
        origin = request.headers.get("origin")
        if origin is not None and origin not in ALLOWED_ORIGINS:       # browsers always send Origin on cross-site POSTs
            raise HTTPException(403, "cross-site request refused")


app = FastAPI(dependencies=[Depends(same_site_only)])


@app.post("/orders/{order_id}/cancel")
def cancel(order_id: int):
    return {"cancelled": order_id}


client = TestClient(app)
print("from our site :", client.post("/orders/42/cancel", headers={"Origin": "https://shop.example"}).status_code)
print("from evil site:", client.post("/orders/42/cancel", headers={"Origin": "https://evil.example"}).status_code)
print("no Origin     :", client.post("/orders/42/cancel").status_code, "(scripts, curl, mobile apps)")
```
```text
from our site : 200
from evil site: 403
no Origin     : 200 (scripts, curl, mobile apps)
```

A request with no `Origin` header is allowed here because non-browser clients do not send one, and a CSRF attack needs a browser. Whether to also demand a token is a risk decision; for cookie-based apps that handle money, do both.

### Try it: spot the flaw

A teammate stores the session id in `localStorage` and sends it in a header from JavaScript, "so CSRF is impossible". True, but what did they give up?

<details><summary>Answer</summary>

They gave up `HttpOnly`. Any JavaScript on the page can read `localStorage`, so one XSS bug (for example an unescaped comment) lets an attacker steal every user's session and use it from anywhere. A cookie flagged `HttpOnly` cannot be read by scripts. The trade is: header tokens in storage avoid CSRF but are exposed to XSS; `HttpOnly` cookies resist XSS theft but need CSRF defences. Choose consciously, and fix XSS either way.

</details>

### Try it: a fixed clock

Write a test showing that a session expires exactly at its `ttl` and not before, using a fake clock. Which two moments do you check?

<details><summary>Answer</summary>

Create the session at `t = 0` with `ttl = 3600`, then check `t = 3600` (still valid, because the code uses `expires < now` as the expiry test) and `t = 3601` (expired). Testing both sides of the boundary catches off-by-one errors (`<` versus `<=`) that sleeping tests never find, and the test runs instantly.

</details>


## 4. Tokens and JWT, beyond the basics

You saw JWT in swe.05 section 12.2. Here we open it up, attack it, and build the part most tutorials skip: refresh tokens that can be revoked.

### 4.1 A JWT built by hand

A JWT is three base64url pieces joined by dots: `header.payload.signature`. The signature for HS256 is an HMAC of the first two pieces. Nothing is encrypted. Building one yourself removes the mystery:

```python run
import base64
import hashlib
import hmac
import json
import warnings

import jwt

warnings.simplefilter("ignore")           # PyJWT warns about short demo keys; we use a long one anyway

KEY = b"a-long-random-demo-key-of-at-least-32-bytes!"


def b64u(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


def b64u_decode(text: str) -> bytes:
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


payload = {"sub": "42", "role": "member", "exp": 2_000_000_000}
header = {"alg": "HS256", "typ": "JWT"}

signing_input = b64u(json.dumps(header, separators=(",", ":")).encode()) + "." + \
                b64u(json.dumps(payload, separators=(",", ":")).encode())
signature = hmac.new(KEY, signing_input.encode(), hashlib.sha256).digest()
mine = signing_input + "." + b64u(signature)

theirs = jwt.encode(payload, KEY, algorithm="HS256")
print("identical to PyJWT's token:", mine == theirs)
print("header  :", json.loads(b64u_decode(mine.split(".")[0])))
print("payload :", json.loads(b64u_decode(mine.split(".")[1])), "<- anyone can read this")
print("verified:", jwt.decode(mine, KEY, algorithms=["HS256"])["sub"])
```
```text
identical to PyJWT's token: True
header  : {'alg': 'HS256', 'typ': 'JWT'}
payload : {'sub': '42', 'role': 'member', 'exp': 2000000000} <- anyone can read this
verified: 42
```

Two facts follow. **The payload is public**: never put passwords, addresses or anything private in a token. And **the signature protects integrity, not secrecy**: change one character in the payload and verification fails, but anyone can read it. (JWE, "encrypted JWT", exists but is rarely needed.)

### 4.2 Claims that must be checked

The registered claims are the standard way to say who, for whom, and until when:

| Claim | Meaning | Check on every request |
|---|---|---|
| `sub` | subject: the user id (a string) | yes |
| `exp` | expiry time | **always**: reject expired tokens |
| `iat`, `nbf` | issued-at, not-before | optional |
| `iss` | issuer: who created the token | when several issuers exist |
| `aud` | audience: which service the token is for | when several services exist |
| `jti` | unique token id | for revocation lists |

A token that was signed by *your* key is not necessarily meant for *this* service. Without `aud` checking, a token from the "reports" service might be accepted by the "payments" service. PyJWT checks `aud`, `iss` and required claims when you ask:

```python run
import warnings
import jwt

warnings.simplefilter("ignore")
KEY = "a-long-random-demo-key-of-at-least-32-bytes!"
good = jwt.encode({"sub": "42", "iss": "pagebound-auth", "aud": "payments", "exp": 2_000_000_000}, KEY, algorithm="HS256")
other = jwt.encode({"sub": "42", "iss": "pagebound-auth", "aud": "reports", "exp": 2_000_000_000}, KEY, algorithm="HS256")
no_exp = jwt.encode({"sub": "42", "iss": "pagebound-auth", "aud": "payments"}, KEY, algorithm="HS256")


def verify(token):
    return jwt.decode(token, KEY, algorithms=["HS256"], audience="payments", issuer="pagebound-auth",
                      options={"require": ["exp", "sub", "iss", "aud"]})


print("good   :", verify(good)["sub"])
for label, bad in (("wrong audience", other), ("no expiry", no_exp)):
    try:
        verify(bad)
    except jwt.PyJWTError as exc:
        print(f"{label:15}", type(exc).__name__)
```
```text
good   : 42
wrong audience  InvalidAudienceError
no expiry       MissingRequiredClaimError
```

Without `options={"require": [...]}`, a token with no `exp` is accepted forever. Make the required claims explicit in one place.

### 4.3 Attacks on JWT you must be able to explain

**Attack 1: `alg: none`.** The header says which algorithm signed the token. A badly written verifier reads that header and believes it. The attacker writes `{"alg":"none"}`, changes the payload to `"role":"admin"`, and sends no signature at all:

```python run
import base64
import hashlib
import hmac
import json
import warnings

import jwt

warnings.simplefilter("ignore")
KEY = b"a-long-random-demo-key-of-at-least-32-bytes!"


def b64u(raw):
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


def b64u_decode(text):
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


def vulnerable_verify(token):
    head, body, sig = token.split(".")
    alg = json.loads(b64u_decode(head))["alg"]               # BUG: trusts the attacker's header
    if alg == "none":
        return json.loads(b64u_decode(body))
    expected = b64u(hmac.new(KEY, f"{head}.{body}".encode(), hashlib.sha256).digest())
    if not hmac.compare_digest(expected, sig):
        raise ValueError("bad signature")
    return json.loads(b64u_decode(body))


forged = b64u(b'{"alg":"none","typ":"JWT"}') + "." + b64u(b'{"sub":"1","role":"admin"}') + "."
print("vulnerable verifier says:", vulnerable_verify(forged))

try:
    jwt.decode(forged, KEY, algorithms=["HS256"])
except jwt.PyJWTError as exc:
    print("PyJWT with algorithms pinned:", type(exc).__name__)
```
```text
vulnerable verifier says: {'sub': '1', 'role': 'admin'}
PyJWT with algorithms pinned: InvalidAlgorithmError
```

The rule: **the server decides the algorithm, never the token.** Always call `jwt.decode(token, key, algorithms=["HS256"])` with the list fixed in your code. (PyJWT 2 refuses to decode without `algorithms`, because of exactly this attack.)

**Attack 2: algorithm confusion.** Services that sign with RS256 (a private key signs, a *public* key verifies) can be fooled if the verifier accepts several algorithms: the attacker signs an HS256 token using the *public* key as the HMAC secret, and a naive verifier uses the same public key as an HS256 secret and accepts it. The same rule prevents it: one algorithm per key, fixed in code. (RS256 needs the `cryptography` package, which is not installed here, so we describe it instead of running it.)

**Attack 3: guessing a weak secret.** An HS256 token can be attacked **offline**: the attacker takes one token and tries candidate secrets until the signature matches. No rate limit applies, because it never touches your server:

```python run
import warnings
import jwt

warnings.simplefilter("ignore")
token = jwt.encode({"sub": "1"}, "summer2024", algorithm="HS256")          # a human-chosen secret

wordlist = ["password", "secret", "admin", "changeme", "summer2024", "qwerty"]    # real lists have millions
for guess in wordlist:
    try:
        jwt.decode(token, guess, algorithms=["HS256"])
        print("secret found:", guess)
        break
    except jwt.InvalidSignatureError:
        pass
```
```text
secret found: summer2024
```

The defence is a secret of at least 32 random bytes (`secrets.token_urlsafe(32)`), which cannot be guessed, kept outside the code (section 15).

**Attack 4 and 5, quick list.** Tokens without `exp` live forever once stolen. Tokens kept in `localStorage` are readable by any XSS bug (section 3, Try it).

### 4.4 Access tokens and refresh tokens

A JWT cannot be "taken back": until `exp`, anyone holding it is let in. So make access tokens **short** (5 to 15 minutes), and pair them with a long-lived **refresh token** (days or weeks) that lives **on the server** and can be revoked. When the access token expires, the client trades the refresh token for a new pair.

The refresh token is the dangerous one, so we add **rotation**: every use returns a *new* refresh token and invalidates the old one. If an old token is ever used again, somebody has a copy, so the whole **family** (all tokens descended from that login) is revoked, forcing a fresh login:

```python run
import hashlib
import secrets


class TokenReuse(Exception):
    pass


class RefreshStore:
    def __init__(self, now, ttl=7 * 86400):
        self.now, self.ttl, self.rows = now, ttl, {}

    @staticmethod
    def _key(token):
        return hashlib.sha256(token.encode()).hexdigest()

    def issue(self, user, family=None):
        token = secrets.token_urlsafe(32)
        self.rows[self._key(token)] = {"user": user, "family": family or secrets.token_hex(8),
                                       "used": False, "expires": self.now() + self.ttl}
        return token

    def rotate(self, token):
        row = self.rows.get(self._key(token))
        if row is None or row["expires"] < self.now():
            raise KeyError("invalid refresh token")
        if row["used"]:                                           # an old token again: theft suspected
            self.rows = {k: v for k, v in self.rows.items() if v["family"] != row["family"]}
            raise TokenReuse("refresh token reused: session revoked")
        row["used"] = True
        return row["user"], self.issue(row["user"], row["family"])


store = RefreshStore(now=lambda: 0)
r1 = store.issue("ada")                                         # at login
user, r2 = store.rotate(r1)                                     # normal refresh
print("rotation gives a new token:", r2 != r1)

try:
    store.rotate(r1)                                            # the thief replays the OLD token
except TokenReuse as exc:
    print("thief:", exc)

try:
    store.rotate(r2)                                            # the real user is logged out too, safely
except KeyError as exc:
    print("real user must log in again:", exc)
```
```text
rotation gives a new token: True
thief: refresh token reused: session revoked
real user must log in again: 'invalid refresh token'
```

Making the user log in again is the price of safety: you cannot tell the thief from the owner, so you end both sessions.

Other ways to revoke access tokens before they expire:

- **Deny-list of `jti`** values (kept in a fast store until the token's `exp`); checked on every request. Costs a lookup, which gives away part of JWT's "no server state" advantage.
- **A version number per user** (`token_version` in the users table and in the token's claims); bump it to invalidate every token of that user at once ("log out everywhere", password change).
- Keep access tokens so short that you do not need either.

### 4.5 A token API, end to end

```python run
import time
import warnings

import jwt
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.testclient import TestClient

warnings.simplefilter("ignore")
SECRET = "a-long-random-demo-key-of-at-least-32-bytes!"
ACCESS_TTL = 600
bearer = HTTPBearer(auto_error=False)
app = FastAPI()


def make_access_token(user_id: str) -> str:
    now = int(time.time())
    return jwt.encode({"sub": user_id, "iat": now, "exp": now + ACCESS_TTL, "aud": "pagebound-api"}, SECRET, algorithm="HS256")


def current_user(creds: HTTPAuthorizationCredentials | None = Depends(bearer)) -> str:
    unauthorised = HTTPException(401, "invalid or missing token", headers={"WWW-Authenticate": "Bearer"})
    if creds is None:
        raise unauthorised
    try:
        claims = jwt.decode(creds.credentials, SECRET, algorithms=["HS256"], audience="pagebound-api",
                            options={"require": ["exp", "sub", "aud"]})
    except jwt.PyJWTError:
        raise unauthorised from None                 # one answer for every failure: do not explain to attackers
    return claims["sub"]


@app.post("/token")
def token(username: str, password: str):
    if (username, password) != ("ada", "right"):
        raise HTTPException(401, "invalid username or password")
    return {"access_token": make_access_token("1"), "token_type": "bearer", "expires_in": ACCESS_TTL}


@app.get("/me")
def me(user_id: str = Depends(current_user)):
    return {"user_id": user_id}


c = TestClient(app)
tok = c.post("/token", params={"username": "ada", "password": "right"}).json()
print(tok["token_type"], tok["expires_in"])
print("with token   :", c.get("/me", headers={"Authorization": f"Bearer {tok['access_token']}"}).json())
r = c.get("/me")
print("no token     :", r.status_code, r.headers["www-authenticate"])
print("garbage token:", c.get("/me", headers={"Authorization": "Bearer abc.def.ghi"}).status_code)
```
```text
bearer 600
with token   : {'user_id': '1'}
no token     : 401 Bearer
garbage token: 401
```

Details worth copying: the `401` carries a `WWW-Authenticate: Bearer` header (required by the standard so clients know which scheme to use), every failure gives the same answer, and `aud` and `exp` are required.

### 4.6 Sessions or tokens? A decision, not a fashion

| Question | Server-side session cookie | Short JWT + refresh token |
|---|---|---|
| Browser site you also render (HTML) | **best choice** | works, more moving parts |
| Mobile app or single-page app calling an API | possible | **common** |
| Several services must accept the same login | needs a shared session store | **natural** (verify with a public key) |
| Instant revocation | **easy** | needs deny-list, version or very short life |
| Where the credential lives in a browser | `HttpOnly` cookie | memory, or an `HttpOnly` cookie; **avoid `localStorage`** |
| CSRF risk | yes: defend (section 3.5) | not for header tokens |

Neither is "more secure" in general. JWT is not an upgrade over sessions; it is a different set of trade-offs.

### Try it: what is wrong with this token?

`{"sub": "42", "is_admin": true}` signed with HS256 and no `exp`. List every problem.

<details><summary>Answer</summary>

(1) No `exp`: valid forever once stolen. (2) `is_admin` inside the token: the role was fixed at login, so if the user is demoted the token still says admin until expiry. Better to load roles from the database on each request, or keep tokens short and re-read roles at refresh. (3) No `aud`/`iss`: another service's token with the same key would pass. (4) If the verifier does not pin `algorithms`, `alg: none` may bypass it. (5) A claim like `is_admin` is also what an attacker would try to forge, so it must never be trusted unless the signature is verified with a fixed algorithm.

</details>

## 5. OAuth2 and OpenID Connect

### 5.1 The problem

You want a photo-printing site to read your photos from a storage service. The old way: give the printing site your storage *password*. Now it can do anything as you, forever, and you cannot take access back without changing your password. **OAuth2** solves this with **delegated access**: the storage service issues the printing site a limited, revocable **access token** after you approve it.

| Role | Who | In the example |
|---|---|---|
| **Resource owner** | the user | you |
| **Client** | the app that wants access | the printing site |
| **Authorization server** | issues tokens after the user agrees | the storage service's login/consent |
| **Resource server** | the API that holds the data | the photo API |

OAuth2 defines several **flows** (called grants):

| Flow | Use | Status |
|---|---|---|
| **Authorization code + PKCE** | apps with a user: web, single-page, mobile | the standard choice |
| **Client credentials** | service to service, no user | standard |
| **Device code** | TVs and consoles | standard |
| Implicit, password grant | old browser apps | **discouraged / removed** in OAuth 2.1 |

### 5.2 Authorization code flow with PKCE

```text
 User/browser          Client app                Authorization server        Resource server
     |  click "connect"    |                              |                        |
     |<--- redirect -------|  /authorize?client_id=..&redirect_uri=..&scope=..
     |                     |   &state=S&code_challenge=C&code_challenge_method=S256
     |----------------------------- user logs in, approves ------->|
     |<---------- redirect to redirect_uri?code=CODE&state=S ------|
     |--- (browser hands the code to the client) -->|
     |                     |-- POST /token: code + code_verifier V -->|
     |                     |<-- access_token (and maybe refresh) -----|
     |                     |------------- GET /photos, Bearer token ------------->|
```

Why each piece exists:

- **`redirect_uri`**: where the code is sent. The server must compare it **exactly** with the one registered for the client, otherwise an attacker redirects the code to their own site.
- **`state`**: a random value the client creates and checks when the user returns. It ties the response to a request *this* browser started and blocks login-CSRF.
- **`code`**: short-lived (about a minute), single-use, bound to the client and the redirect. It travels through the browser, so it is exposed; it is useless on its own.
- **PKCE** (Proof Key for Code Exchange, "pixie"): the client creates a secret `code_verifier` V, sends only its hash `code_challenge` C at the start, and sends V itself at the token step. A thief who steals the *code* from the redirect cannot redeem it without V. PKCE is required for public clients (mobile and single-page apps, which cannot keep a client secret) and recommended for all.
- **`scope`**: what the token may do, such as `photos:read`. The resource server enforces it.

The PKCE maths is two lines. The RFC 7636 test vector lets you check your implementation:

```python run
import base64
import hashlib
import secrets


def make_verifier() -> str:
    return secrets.token_urlsafe(48)                       # 64 characters; the RFC allows 43 to 128


def challenge_for(verifier: str) -> str:
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b"=").decode()


# the example from RFC 7636, appendix B
print(challenge_for("dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk"))
v = make_verifier()
print(len(v), "chars | challenge is", len(challenge_for(v)), "chars | verifier not derivable from it")
```
```text
E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM
64 chars | challenge is 43 chars | verifier not derivable from it
```

### 5.3 A tiny authorization server and client, in one process

To see the rules enforced, here is a miniature authorization server (`/authorize`, `/token`) and resource server (`/photos`). A real server shows a login and consent page; we assume the user "ada" has already logged in and approved:

```python
# oauth_demo.py
import base64
import hashlib
import secrets
import time
import warnings
from urllib.parse import parse_qs, urlencode, urlparse

import jwt
from fastapi import FastAPI, Form, Header, HTTPException, Query
from fastapi.responses import RedirectResponse

warnings.simplefilter("ignore")
SIGNING_KEY = "oauth-demo-signing-key-at-least-32-bytes-long!"
CLIENTS = {"printshop": {"redirect_uris": {"https://print.example/callback"}, "scopes": {"photos:read"}}}
codes: dict[str, dict] = {}


def s256(verifier: str) -> str:
    return base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()


auth_server = FastAPI()


@auth_server.get("/authorize")
def authorize(client_id: str, redirect_uri: str, response_type: str, scope: str, state: str,
              code_challenge: str, code_challenge_method: str):
    client = CLIENTS.get(client_id)
    if client is None or redirect_uri not in client["redirect_uris"]:        # EXACT match, never a prefix
        raise HTTPException(400, "unknown client or redirect_uri")           # never redirect to an unverified URI
    if response_type != "code" or code_challenge_method != "S256":
        raise HTTPException(400, "only response_type=code with PKCE S256 is supported")
    if not set(scope.split()) <= client["scopes"]:
        raise HTTPException(400, "scope not allowed for this client")
    code = secrets.token_urlsafe(24)
    codes[code] = {"client_id": client_id, "redirect_uri": redirect_uri, "challenge": code_challenge,
                   "scope": scope, "user": "ada", "expires": time.time() + 60}
    return RedirectResponse(f"{redirect_uri}?{urlencode({'code': code, 'state': state})}", status_code=302)


@auth_server.post("/token")
def token(grant_type: str = Form(), code: str = Form(), redirect_uri: str = Form(),
          client_id: str = Form(), code_verifier: str = Form()):
    entry = codes.pop(code, None)                                            # pop: a code works once
    bad = HTTPException(400, {"error": "invalid_grant"})
    if entry is None or entry["expires"] < time.time():
        raise bad
    if entry["client_id"] != client_id or entry["redirect_uri"] != redirect_uri:
        raise bad
    if not secrets.compare_digest(s256(code_verifier), entry["challenge"]):   # PKCE check
        raise bad
    now = int(time.time())
    access = jwt.encode({"sub": entry["user"], "scope": entry["scope"], "aud": "photo-api", "iss": "auth.example",
                         "iat": now, "exp": now + 600}, SIGNING_KEY, algorithm="HS256")
    return {"access_token": access, "token_type": "Bearer", "expires_in": 600, "scope": entry["scope"]}


resource_server = FastAPI()


@resource_server.get("/photos")
def photos(authorization: str = Header(default="")):
    try:
        claims = jwt.decode(authorization.removeprefix("Bearer "), SIGNING_KEY, algorithms=["HS256"],
                            audience="photo-api", issuer="auth.example", options={"require": ["exp", "sub", "scope"]})
    except jwt.PyJWTError:
        raise HTTPException(401, "invalid token", headers={"WWW-Authenticate": "Bearer"}) from None
    if "photos:read" not in claims["scope"].split():                         # scope enforcement
        raise HTTPException(403, "insufficient_scope")
    return {"owner": claims["sub"], "photos": ["cat.jpg", "dog.jpg"]}
```

Now play the client. We run the whole dance, then replay it with each attack:

```python run
import secrets
from urllib.parse import parse_qs, urlparse

from fastapi.testclient import TestClient

import oauth_demo as o

auth, api = TestClient(o.auth_server), TestClient(o.resource_server)
REDIRECT = "https://print.example/callback"


def start(**changes):
    """Client side: create state and PKCE values, then call /authorize."""
    verifier, state = secrets.token_urlsafe(48), secrets.token_urlsafe(16)
    params = dict(client_id="printshop", redirect_uri=REDIRECT, response_type="code", scope="photos:read",
                  state=state, code_challenge=o.s256(verifier), code_challenge_method="S256") | changes
    return verifier, state, auth.get("/authorize", params=params, follow_redirects=False)


def redeem(code, verifier, **changes):
    data = dict(grant_type="authorization_code", code=code, redirect_uri=REDIRECT, client_id="printshop",
                code_verifier=verifier) | changes
    return auth.post("/token", data=data)


# 1. the happy path
verifier, state, r = start()
back = parse_qs(urlparse(r.headers["location"]).query)
print("redirected:", r.status_code, "| state echoed back correctly:", back["state"][0] == state)
tok = redeem(back["code"][0], verifier).json()
print("token scope:", tok["scope"], "->", api.get("/photos", headers={"Authorization": f"Bearer {tok['access_token']}"}).json())

# 2. attacker steals the code from the redirect but does not know the verifier
verifier, state, r = start()
stolen = parse_qs(urlparse(r.headers["location"]).query)["code"][0]
print("stolen code, wrong verifier :", redeem(stolen, secrets.token_urlsafe(48)).status_code)

# 3. the code was already redeemed (replay)
verifier, state, r = start()
code = parse_qs(urlparse(r.headers["location"]).query)["code"][0]
redeem(code, verifier)
print("same code twice             :", redeem(code, verifier).status_code)

# 4. a client tries to use a redirect_uri it did not register
_, _, r = start(redirect_uri="https://evil.example/callback")
print("unregistered redirect_uri   :", r.status_code)
_, _, r = start(redirect_uri=REDIRECT + "/../x")
print("near-match redirect_uri     :", r.status_code)

# 5. scope is enforced by the resource server
print("no token                    :", api.get("/photos").status_code)
import jwt
weak = jwt.encode({"sub": "ada", "scope": "profile", "aud": "photo-api", "iss": "auth.example", "exp": 2_000_000_000}, o.SIGNING_KEY, algorithm="HS256")
print("valid token, wrong scope    :", api.get("/photos", headers={"Authorization": f"Bearer {weak}"}).status_code)
```
```text
redirected: 302 | state echoed back correctly: True
token scope: photos:read -> {'owner': 'ada', 'photos': ['cat.jpg', 'dog.jpg']}
stolen code, wrong verifier : 400
same code twice             : 400
unregistered redirect_uri   : 400
near-match redirect_uri     : 400
no token                    : 401
valid token, wrong scope    : 403
```

The most important outputs are the `400`s: **a stolen code is useless without the verifier**, a code works **once**, and a redirect must match **exactly** (a "starts with" or pattern match lets an attacker use `https://print.example.evil.com`, or an open redirect on a registered domain). Note the last line: a token that is valid but lacks the scope gets **`403`**, not `401`: the caller is known, but not allowed.

### 5.4 OpenID Connect: logging in with another account

OAuth2 answers "may this app access that API?" It does **not** say who the user is. **OpenID Connect (OIDC)** adds an identity layer on top: ask for the `openid` scope and the server also returns an **ID token**, a JWT whose claims say who just authenticated. "Log in with Google/GitHub/Microsoft" is OIDC (GitHub uses its own variation).

The client must validate the ID token before trusting it:

| Check | Why |
|---|---|
| signature, with the provider's public keys (fetched from its **JWKS** URL), algorithm fixed | it came from the provider |
| `iss` equals the provider's issuer | right provider |
| `aud` contains **your** client id | the token was meant for you, not another app |
| `exp` in the future | not stale |
| `nonce` equals the one you sent | not replayed from another login |

An access token is **not** a proof of login: it is a key to an API, possibly issued to some other app. Use the ID token to identify the user, and the access token to call APIs. After validation, identify the user by the pair `(iss, sub)`, which never changes, not by e-mail.

Here is the claims check, with the signature part simplified to HS256 (real providers use RS256 with a JWKS endpoint):

```python run
import time
import warnings

import jwt

warnings.simplefilter("ignore")
KEY = "provider-signing-key-at-least-32-bytes-long!!"
MY_CLIENT_ID, MY_NONCE, ISSUER = "printshop", "n-0S6_WzA2Mj", "https://accounts.example"


def validate_id_token(token: str) -> dict:
    claims = jwt.decode(token, KEY, algorithms=["HS256"], audience=MY_CLIENT_ID, issuer=ISSUER,
                        options={"require": ["exp", "sub", "iss", "aud", "nonce"]})
    if claims["nonce"] != MY_NONCE:
        raise ValueError("nonce mismatch: replayed token")
    return claims


def issue(**changes):
    now = int(time.time())
    claims = {"iss": ISSUER, "aud": MY_CLIENT_ID, "sub": "10769150350006150715113082367", "exp": now + 300,
              "nonce": MY_NONCE, "email": "ada@example.com", "email_verified": True} | changes
    return jwt.encode(claims, KEY, algorithm="HS256")


print("valid       :", validate_id_token(issue())["sub"])
for label, token in (("other app", issue(aud="otherapp")), ("other issuer", issue(iss="https://evil.example")),
                     ("replayed", issue(nonce="old-nonce"))):
    try:
        validate_id_token(token)
    except (jwt.PyJWTError, ValueError) as exc:
        print(f"{label:12}:", type(exc).__name__)
```
```text
valid       : 10769150350006150715113082367
other app   : InvalidAudienceError
other issuer: InvalidIssuerError
replayed    : ValueError
```

### 5.5 Mistakes that cause real account takeovers

- **Linking accounts by e-mail alone.** A site lets users "log in with Provider X" and merges them into the local account with the same e-mail. An attacker creates an account at a weak provider using the victim's e-mail address *unverified*, and the site logs them into the victim's account. Rule: trust an e-mail only if `email_verified` is true, and from a provider you trust; key identities on `(iss, sub)`.
- **A loose `redirect_uri`** (prefix or wildcard match) or an open redirect on a registered domain.
- **No `state`** (login CSRF) or not checking it on return.
- **No PKCE** for mobile or single-page apps; using the old implicit flow.
- **Tokens in `localStorage`**; very long-lived access tokens.
- **Skipping `aud` and `iss` checks**, so a token for another app is accepted.
- **Building your own authorization server** for a product that could use a maintained one (Keycloak, Authentik, a cloud identity service). OAuth2 has many sharp edges.

> **Try it on your machine**: use a maintained library and a real provider.
>
> ```bash
> pip install authlib httpx
> ```
>
> With Authlib you register a client at your provider (a GitHub OAuth app, a Google Cloud OAuth client), set the redirect URL to `http://127.0.0.1:8000/callback`, and use `oauth.register(..., server_metadata_url=...)`. The library creates `state`, `nonce` and PKCE for you, and validates the ID token against the provider's JWKS. The details change between providers and versions, so follow the library's current documentation.

### Try it: the sloppy redirect check

A server validates `redirect_uri` with `redirect_uri.startswith("https://print.example")`. Give one URL that passes and sends the code to an attacker.

<details><summary>Answer</summary>

`https://print.example.evil.com/callback` starts with the registered text, so the check passes, and the authorization code is delivered to `evil.com`. Another is `https://print.example@evil.com/` (the part before `@` is treated as user info). The fix: compare the *whole string* to a registered value (`redirect_uri in client["redirect_uris"]`), as the demo does. PKCE reduces the damage of a stolen code, but never rely on one layer.

</details>

## 6. API keys, one-time codes and signed webhooks

OAuth2 is for users delegating access. Three other everyday mechanisms are simpler.

### 6.1 API keys

An **API key** identifies a *program* (a customer's script, a partner's server). It is a long random string the customer sends in a header (`X-API-Key: ...` or `Authorization: Bearer ...`). Rules for doing it safely:

- **Generate** with `secrets.token_urlsafe(32)`, never `random`.
- **Show the key once** at creation, like a password. Store only a **hash** (SHA-256 is fine because the key has 256 bits of randomness, so nobody can guess it, which is different from human passwords).
- Add a **non-secret prefix** (`pgb_live_AbC123...`). It lets you find the row quickly, show "key ending ...x9f2" in a dashboard, and lets secret scanners (GitHub's included) recognise a leaked key by its shape.
- Attach **scopes** and an **owner**, so a key can be read-only and traced to a customer.
- Support **rotation** (two active keys at once while the customer switches), **revocation** and a **last used** time.
- **Never in URLs**: query strings land in logs, browser history and referrer headers.

```python run
import hashlib
import hmac
import secrets


class ApiKeys:
    def __init__(self):
        self.rows = {}                                             # prefix -> record

    def create(self, owner: str, scopes: set[str]) -> str:
        prefix = secrets.token_hex(4)                              # lookup id, not secret
        secret = secrets.token_urlsafe(32)
        self.rows[prefix] = {"owner": owner, "scopes": scopes, "hash": hashlib.sha256(secret.encode()).hexdigest(),
                             "revoked": False}
        return f"pgb_live_{prefix}_{secret}"                      # the only time the full key exists

    def check(self, presented: str, needed: str):
        try:
            _, _, prefix, secret = presented.split("_", 3)
        except ValueError:
            return None
        row = self.rows.get(prefix)
        digest = hashlib.sha256(secret.encode()).hexdigest()
        if row is None or row["revoked"] or not hmac.compare_digest(row["hash"], digest):
            return None
        return row["owner"] if needed in row["scopes"] else None


keys = ApiKeys()
key = keys.create("acme-corp", {"orders:read"})
print("key shape :", key[:9] + "<prefix>_<secret>", "| secret is not stored:", key.split("_", 3)[3] not in str(keys.rows))
print("read      :", keys.check(key, "orders:read"))
print("write     :", keys.check(key, "orders:write"), "(scope missing)")
print("tampered  :", keys.check(key[:-1] + "x", "orders:read"))
keys.rows[key.split("_")[2]]["revoked"] = True
print("revoked   :", keys.check(key, "orders:read"))
```
```text
key shape : pgb_live_<prefix>_<secret> | secret is not stored: True
read      : acme-corp
write     : None (scope missing)
tampered  : None
revoked   : None
```

### 6.2 Machine-to-machine access

For one internal service calling another, prefer **short-lived tokens** to long-lived keys: the OAuth2 *client credentials* grant (the service exchanges its client id and secret for a token valid for minutes). Inside a cluster, **mutual TLS** (both sides present certificates) or a platform identity (cloud IAM roles, Kubernetes service accounts) removes shared secrets altogether. Whatever you choose, give each service its own credential, so one compromise does not unlock everything and you can tell in the logs who did what.

### 6.3 One-time codes: TOTP

**Multi-factor authentication** adds "something you have" to "something you know". The usual app-based method is **TOTP** (RFC 6238): the server and the user's authenticator app share a secret; both compute a 6-digit code from the secret and the current 30-second time slot. The algorithm is 10 lines, and the RFC publishes test values to check it:

```python run
import base64
import hmac
import hashlib
import struct


def hotp(key: bytes, counter: int, digits: int = 6) -> str:
    mac = hmac.new(key, struct.pack(">Q", counter), hashlib.sha1).digest()
    offset = mac[-1] & 0x0F                                          # "dynamic truncation"
    number = struct.unpack(">I", mac[offset:offset + 4])[0] & 0x7FFFFFFF
    return str(number % 10**digits).zfill(digits)


def totp(key: bytes, at: float, step: int = 30, digits: int = 6) -> str:
    return hotp(key, int(at) // step, digits)


RFC_KEY = b"12345678901234567890"
for at, expected in [(59, "94287082"), (1111111109, "07081804"), (2000000000, "69279037")]:
    print(at, totp(RFC_KEY, at, digits=8), "matches RFC:", totp(RFC_KEY, at, digits=8) == expected)


def verify_totp(key: bytes, code: str, now: float, last_step: int = -1, window: int = 1):
    """Accept the current slot and one slot either side (clock drift). Refuse a slot already used."""
    step = int(now) // 30
    for s in range(step - window, step + window + 1):
        if s > last_step and hmac.compare_digest(hotp(key, s), code):
            return s                                                 # remember it as last_step
    return None


secret = base64.b32encode(RFC_KEY).decode()                          # what the QR code carries
print("base32 secret for authenticator apps:", secret[:12] + "...")
now = 1_700_000_000
code = totp(RFC_KEY, now)
used = verify_totp(RFC_KEY, code, now)
print("first use   :", used is not None)
print("replay      :", verify_totp(RFC_KEY, code, now, last_step=used))
print("wrong code  :", verify_totp(RFC_KEY, "000000", now))
```
```text
59 94287082 matches RFC: True
1111111109 07081804 matches RFC: True
2000000000 69279037 matches RFC: True
base32 secret for authenticator apps: GEZDGNBVGY3T...
first use   : True
replay      : None
wrong code  : None
```

Details that matter in production: allow only ±1 time slot, **refuse a code that was already used** (the `last_step` memory above), rate-limit attempts (a 6-digit code has only a million values), give users **recovery codes** (hashed, single-use) and watch the "lost phone" reset path, which attackers target. **Passkeys / WebAuthn** (a phone or security key proves possession using public-key cryptography and refuses to work on a look-alike site) resist phishing better than TOTP; they need browser support and a library, so they are described here only.

### 6.4 Signed webhooks

When your server calls a customer's server (a "webhook": `POST /hooks/payment`), the customer must be sure the request really came from you and was not changed or replayed. Sign it: compute `HMAC-SHA256(secret, timestamp + "." + body)`, send the timestamp and the signature as headers, and have the receiver recompute and compare. Include the timestamp in the signature and reject old ones, otherwise a recorded valid request can be replayed forever. Also remember the **event id** to ignore duplicates.

```python run
import hashlib
import hmac
import json
import time

SECRET = b"whsec_demo_shared_secret"
TOLERANCE = 300                                                      # seconds


def sign(body: bytes, ts: int) -> str:
    return hmac.new(SECRET, f"{ts}.".encode() + body, hashlib.sha256).hexdigest()


seen_events: set[str] = set()


def receive(body: bytes, ts: int, signature: str, now: int):
    if abs(now - ts) > TOLERANCE:
        return "rejected: timestamp outside tolerance (replay?)"
    if not hmac.compare_digest(sign(body, ts), signature):
        return "rejected: bad signature"
    event_id = json.loads(body)["id"]
    if event_id in seen_events:
        return "ok (duplicate event ignored)"
    seen_events.add(event_id)
    return "ok (processed)"


body = json.dumps({"id": "evt_1", "amount": 500}).encode()
now = int(time.time())
sig = sign(body, now)
print("valid    :", receive(body, now, sig, now))
print("duplicate:", receive(body, now, sig, now))
print("tampered :", receive(body.replace(b"500", b"900"), now, sig, now))
print("old      :", receive(body, now - 3600, sign(body, now - 3600), now))
```
```text
valid    : ok (processed)
duplicate: ok (duplicate event ignored)
tampered : rejected: bad signature
old      : rejected: timestamp outside tolerance (replay?)
```

Sign the **raw bytes** you received: parsing the JSON and re-serialising it can change spacing and key order, and break the match. This is the same scheme payment providers use for their webhooks.

### Try it: why SHA-256 for keys but scrypt for passwords?

Both are secrets you store as hashes. Why is a fast hash acceptable for API keys but not for passwords?

<details><summary>Answer</summary>

Guessing speed only matters when the secret is guessable. A password chosen by a human comes from a small set of likely values, so an attacker with the hash tries billions of candidates per second unless the hash is slow. An API key is 256 random bits: there are 2^256 possibilities, so even at a trillion guesses per second the search never finishes. The hash only needs to keep a stolen database from revealing the key itself, which SHA-256 does. (A slow hash on every API request would also be an easy way to overload your own server.)

</details>

### Try it: the TOTP replay

An attacker watches over a user's shoulder and types the code they see 10 seconds after the user logs in, within the same 30-second slot. What stops it?

<details><summary>Answer</summary>

Remembering the last accepted time slot per user (`last_step`) and refusing any code from that slot or an earlier one. The code is still arithmetically valid, so only server-side memory rejects it. It also helps to bind the second step to the same login attempt and to rate-limit failures.

</details>


## 7. Authorisation: roles, ownership and policies

Authentication ended with "this request comes from user 1". Authorisation asks the harder question: **may user 1 do this, to this object, right now?** Most serious API breaches are failures here, not in cryptography.

### 7.1 Three levels of "may they?"

| Level | Question | Typical bug | Name in the OWASP API list |
|---|---|---|---|
| **Function level** | may this *kind* of user call this endpoint? | a normal user calls `/admin/users` | broken function level authorisation (BFLA) |
| **Object level** | may this user touch *this particular* object? | user 1 reads order 3, which belongs to user 2 | broken object level authorisation (BOLA), also called **IDOR** |
| **Property level** | may they see or change *this field* of the object? | a user sets `role = "admin"` on their own profile; the response includes `password_hash` | broken object property level authorisation (mass assignment, excessive data exposure) |

Every endpoint needs all three answered. Missing the second one is the commonest bug in real APIs, and section 8 is about it.

### 7.2 Models for deciding

| Model | Idea | Good for | Weakness |
|---|---|---|---|
| **Ownership** | the object has an `owner_id`; only the owner (plus staff) may act | "my orders", "my notes" | does not express teams or sharing |
| **RBAC** (role-based) | users have roles; roles have permissions (`support` may `order:read`) | admin, support, customer | role explosion; cannot say "only orders under 100" |
| **ABAC** (attribute-based) | rules over attributes of user, object and context (amount, department, time) | refund limits, "same department" | rules spread around the code if not centralised |
| **Scopes** | a token carries the permissions the user gave it (`photos:read`) | OAuth2, API keys | scopes limit a *token*; they do not replace checks on the *user* |
| **ReBAC** (relationship-based) | permission follows relationships ("member of the team that owns the project") | documents, projects, sharing | needs a relationship store; libraries exist |

Real systems combine them: *the order must be mine (ownership) or I must be support (role), and a refund over 100 EUR needs an admin (attribute).*

### 7.3 One policy function, deny by default

Scattered `if user.role == "admin"` lines get out of date and cannot be tested. Put the decisions in **one place**, as plain Python that does not know about HTTP. The rule engine below is only 25 lines, and it is testable without a web server:

```python
# policy.py
from dataclasses import dataclass


@dataclass(frozen=True)
class User:
    id: int
    role: str                      # "customer" | "support" | "admin"


@dataclass(frozen=True)
class Order:
    id: int
    owner_id: int
    status: str
    total_cents: int


REFUND_LIMIT_FOR_SUPPORT = 10_000          # 100.00 in cents


def can(user: User | None, action: str, order: Order | None = None, *, amount: int = 0) -> bool:
    """Return True only if a rule below explicitly allows it. The last line is the deny-by-default."""
    if user is None:
        return False
    if user.role == "admin":
        return action in {"read", "cancel", "refund", "list_all"}
    if user.role == "support":
        if action in {"read", "list_all"}:
            return True
        if action == "refund":
            return order is not None and amount <= REFUND_LIMIT_FOR_SUPPORT
        return False
    if user.role == "customer":
        if order is None:
            return False
        owns = order.owner_id == user.id
        if action == "read":
            return owns
        if action == "cancel":
            return owns and order.status == "pending"
        return False
    return False                                     # unknown role: deny
```

Test it as a table. A grid like this is the best documentation of your security rules, and reviewers can read it in a minute:

```python run
from policy import Order, User, can

ada, bo = User(1, "customer"), User(2, "customer")
sam, root = User(3, "support"), User(4, "admin")
pending = Order(10, owner_id=1, status="pending", total_cents=2500)
paid = Order(11, owner_id=1, status="paid", total_cents=2500)

rows = [
    ("owner reads own order", ada, "read", pending, True),
    ("other customer reads it", bo, "read", pending, False),
    ("owner cancels pending", ada, "cancel", pending, True),
    ("owner cancels paid", ada, "cancel", paid, False),
    ("support reads any", sam, "read", pending, True),
    ("support cancels", sam, "cancel", pending, False),
    ("support small refund", sam, "refund", paid, True),
    ("anonymous reads", None, "read", pending, False),
    ("customer lists all", ada, "list_all", None, False),
    ("admin lists all", root, "list_all", None, True),
    ("unknown action", root, "format_disk", pending, False),
]
bad = 0
for label, user, action, order, expected in rows:
    got = can(user, action, order)
    bad += got != expected
    print(f"{'ok ' if got == expected else 'BAD'} {label:26} -> {got}")
print("support refund of 150.00:", can(sam, "refund", paid, amount=15_000), "| of 50.00:", can(sam, "refund", paid, amount=5_000))
print("mismatches:", bad)
```
```text
ok  owner reads own order      -> True
ok  other customer reads it    -> False
ok  owner cancels pending      -> True
ok  owner cancels paid         -> False
ok  support reads any          -> True
ok  support cancels            -> False
ok  support small refund       -> True
ok  anonymous reads            -> False
ok  customer lists all         -> False
ok  admin lists all            -> True
ok  unknown action             -> False
support refund of 150.00: False | of 50.00: True
mismatches: 0
```

The `refund` rule shows ABAC (the amount decides), `cancel` mixes ownership and state, and the final `return False` is **deny by default**: a typo in an action name or a new role gets *no* access, never accidental access.

### 7.4 Where to enforce, and how not to forget

The policy says what is allowed. You still must **call** it on every route. Three habits make forgetting hard:

1. **Authenticate by default.** Put the authentication dependency on the whole app and keep an explicit list of the few public routes (`/login`, `/health`). A new route is then protected unless someone deliberately opens it.
2. **Authorise in the data access.** Load objects through a function that takes the user (`orders.get_for(user, order_id)`), so the query itself is scoped (section 8). Do not fetch by id and "remember to check" afterwards.
3. **Test the matrix.** A test per rule (above), and a test that walks every route (section 8.4).

```python run
from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.testclient import TestClient

PUBLIC_PATHS = {"/health", "/login"}                      # the reviewed list of routes that need no login


def require_login(request: Request, authorization: str = Header(default="")):
    if request.scope["route"].path in PUBLIC_PATHS:
        return
    if authorization != "Bearer good":
        raise HTTPException(401, "login required", headers={"WWW-Authenticate": "Bearer"})


app = FastAPI(dependencies=[Depends(require_login)])       # applies to EVERY route of the app


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/orders")
def orders():
    return []


@app.get("/new-route-the-developer-forgot-to-protect")
def forgotten():
    return {"secret": "data"}


c = TestClient(app)
print("orders, no token   :", c.get("/orders").status_code)
print("forgotten, no token:", c.get("/new-route-the-developer-forgot-to-protect").status_code, "<- protected by default")
print("health, no token   :", c.get("/health").status_code, "<- public on purpose")
print("forgotten, token   :", c.get("/new-route-the-developer-forgot-to-protect", headers={"Authorization": "Bearer good"}).status_code)
```
```text
orders, no token   : 401
forgotten, no token: 401 <- protected by default
health, no token   : 200 <- public on purpose
forgotten, token   : 200
```

The developer who forgot to think about security still got a protected route. Making a route public now needs an edit to `PUBLIC_PATHS`, a single, reviewable place, and a test (section 8.4) can compare the app's routes with that list. This is the "fail closed" principle in code.

### 7.5 401, 403 or 404?

| Situation | Status | Why |
|---|---|---|
| no credentials, or invalid ones | **401** + `WWW-Authenticate` | "I do not know who you are" |
| known user, action not allowed on something that is public knowledge | **403** | "I know you, and no" |
| known user, object **belongs to someone else** | **404** | do not even confirm that the object exists |
| role missing for an admin-only endpoint | **403** | the endpoint exists publicly, only the permission is missing |

Answering `403` for "that order exists but is not yours" tells an attacker which ids are real. Answering `404` for both "does not exist" and "not yours" gives them nothing. Choose one rule and apply it everywhere.

### 7.6 Multi-tenant systems

If one database serves many customers (companies), every table carries a `tenant_id`, and **every** query must filter on it. One forgotten `WHERE tenant_id = ?` leaks one company's data to another, a disaster for a business-to-business product. Make it hard to forget: a single data-access function that always adds the tenant filter, tests with two tenants, and where your database supports it **row-level security** (PostgreSQL's `CREATE POLICY ... USING (tenant_id = current_setting('app.tenant')::int)`), so that even a buggy query cannot cross the line. RLS is described here rather than run, because SQLite has no such feature.

### Try it: read the policy

Using `can()` above, would a *support* user be allowed to `cancel` an order? Which line decides, and what is your reaction if a manager asks you to "just let support cancel too"?

<details><summary>Answer</summary>

No: in the `support` branch, `read`, `list_all` and `refund` are listed and everything else falls to `return False`. To allow cancelling you add `"cancel"` to the support rules and one row to the test table. The point of a central policy is that this is a *reviewable one-line change* with a test, not a hunt through 40 route functions. Also ask what limits apply (only pending orders? an audit log entry?).

</details>

## 8. Object-level authorisation: stopping IDOR, and testing it

This section delivers the first outcome of the chapter: **prevent a user from reading another user's data, and prove that it is prevented with a test.**

### 8.1 The bug in one endpoint

**IDOR** (insecure direct object reference), called **BOLA** in the OWASP API list, means the API takes an id from the client and uses it without asking whether this user may access that object. The code below is a complete small API. It has a flag, `secure`: with `secure=False` it contains several classic bugs, with `secure=True` the fixes. Read the `if secure:` branches as "what the fix looks like".

```python
# pagebound.py
import sqlite3

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, ConfigDict

TOKENS = {"t-ada": 1, "t-bo": 2, "t-sam": 3, "t-root": 4}     # stand-in for the real login of sections 2 to 4


def make_db():
    db = sqlite3.connect(":memory:", check_same_thread=False)
    db.row_factory = sqlite3.Row
    db.executescript("""
        CREATE TABLE users  (id INTEGER PRIMARY KEY, name TEXT, role TEXT, password_hash TEXT);
        CREATE TABLE orders (id INTEGER PRIMARY KEY, owner_id INTEGER NOT NULL REFERENCES users(id),
                             total_cents INTEGER NOT NULL, status TEXT NOT NULL DEFAULT 'pending', note TEXT DEFAULT '');
        INSERT INTO users VALUES (1,'ada','customer','scrypt$16384$8$1$AAAA$BBBB'), (2,'bo','customer','scrypt$16384$8$1$CCCC$DDDD'),
                                 (3,'sam','support','scrypt$16384$8$1$EEEE$FFFF'), (4,'root','admin','scrypt$16384$8$1$GGGG$HHHH');
        INSERT INTO orders (owner_id, total_cents, status, note) VALUES
            (1, 2500, 'pending', ''), (1, 990, 'paid', ''), (2, 4200, 'pending', 'gift for mom'), (2, 150, 'paid', '');
    """)
    return db


class ProfileUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")              # unknown fields are an error, not ignored
    name: str


def build_app(secure: bool = True) -> FastAPI:
    db, app = make_db(), FastAPI()

    def current_user(authorization: str = Header(default="")) -> dict:
        user_id = TOKENS.get(authorization.removeprefix("Bearer "))
        if user_id is None:
            raise HTTPException(401, "invalid or missing token", headers={"WWW-Authenticate": "Bearer"})
        return dict(db.execute("SELECT id, name, role FROM users WHERE id = ?", (user_id,)).fetchone())

    @app.get("/orders/{order_id}")
    def get_order(order_id: int, user: dict = Depends(current_user)):
        sql, args = "SELECT * FROM orders WHERE id = ?", [order_id]
        if secure and user["role"] == "customer":
            sql += " AND owner_id = ?"                       # FIX: the query itself is scoped to the caller
            args.append(user["id"])
        row = db.execute(sql, args).fetchone()
        if row is None:
            raise HTTPException(404, "order not found")      # same answer for "missing" and "not yours"
        return dict(row)

    @app.post("/orders/{order_id}/cancel")
    def cancel_order(order_id: int, user: dict = Depends(current_user)):
        sql, args = "UPDATE orders SET status = 'cancelled' WHERE id = ? AND status = 'pending'", [order_id]
        if secure:
            sql += " AND owner_id = ?"                       # FIX: a write must be scoped as well
            args.append(user["id"])
        cur = db.execute(sql, args)
        db.commit()
        if cur.rowcount == 0:
            raise HTTPException(404, "order not found")
        return {"cancelled": order_id}

    @app.get("/admin/users")
    def admin_users(user: dict = Depends(current_user)):
        if secure and user["role"] != "admin":
            raise HTTPException(403, "admins only")          # FIX: function-level check
        columns = "id, name, role" if secure else "*"        # FIX: never select what you will not return
        return [dict(r) for r in db.execute(f"SELECT {columns} FROM users")]

    body_type = ProfileUpdate if secure else dict          # FIX: a model with an allow-list of writable fields

    @app.patch("/users/me")
    def update_me(body: body_type, user: dict = Depends(current_user)):
        if secure:
            body = body.model_dump()
        for column, value in body.items():                   # BUG when not secure: any column, including "role"
            if column in {"name", "role"}:
                db.execute(f"UPDATE users SET {column} = ? WHERE id = ?", (value, user["id"]))
        db.commit()
        return dict(db.execute("SELECT id, name, role FROM users WHERE id = ?", (user["id"],)).fetchone())

    return app
```

Now attack the version with the bugs, as user **ada** (token `t-ada`). Orders 1 and 2 are hers; orders 3 and 4 belong to **bo**:

```python run
from fastapi.testclient import TestClient

from pagebound import build_app

client = TestClient(build_app(secure=False))
ada = {"Authorization": "Bearer t-ada"}

print("ada reads her order 1 :", client.get("/orders/1", headers=ada).json())
stolen = client.get("/orders/3", headers=ada)                      # just change the number
print("ada reads bo's order 3:", stolen.status_code, stolen.json())

print("ada cancels bo's order:", client.post("/orders/3/cancel", headers=ada).json())
print("bo's order now        :", client.get("/orders/3", headers={"Authorization": "Bearer t-bo"}).json()["status"])

print("ada lists all users   :", client.get("/admin/users", headers=ada).json()[0])
print("ada makes herself admin:", client.patch("/users/me", json={"role": "admin"}, headers=ada).json())
```
```text
ada reads her order 1 : {'id': 1, 'owner_id': 1, 'total_cents': 2500, 'status': 'pending', 'note': ''}
ada reads bo's order 3: 200 {'id': 3, 'owner_id': 2, 'total_cents': 4200, 'status': 'pending', 'note': 'gift for mom'}
ada cancels bo's order: {'cancelled': 3}
bo's order now        : cancelled
ada lists all users   : {'id': 1, 'name': 'ada', 'role': 'customer', 'password_hash': 'scrypt$16384$8$1$AAAA$BBBB'}
ada makes herself admin: {'id': 1, 'name': 'ada', 'role': 'admin'}
```

All four attacks worked, and none needed a clever trick, only a changed number or an extra field. Notice what **did** work correctly: every request was authenticated. IDOR is not an authentication failure; it is the absence of the question "whose is this?". Also note the `password_hash` column in the admin listing: even the legitimate admin should never receive it.

### 8.2 Why random ids are not the fix

A common reaction is "use UUIDs, so nobody can guess the next id". Random ids help a little (a scanner cannot walk `1, 2, 3...`), but they are **not** an authorisation check. Ids leak constantly: in URLs shared by chat, in logs, in referrer headers, in an e-mail a former employee still has. If the only protection is that the id is hard to guess, anyone who learns one id has the data. Use unguessable ids if you like (they reduce exposure), and **also** check ownership.

### 8.3 The fix: scope the query, return 404

The fixes in the code above, in order of preference:

1. **Scope the query by the caller** (`WHERE id = ? AND owner_id = ?`). The database refuses to find another user's row. This works for reads, updates and deletes alike, and cannot be forgotten halfway: there is no "fetch first, check later" gap.
2. **Fetch, then ask the policy** (`can(user, "read", order)`), and answer `404` or `403`. Needed when the rule depends on attributes (section 7.3).
3. **Database row-level security** as a safety net behind both.

Whichever you choose, return **404** for "not yours", so that you do not confirm that the object exists. Now the same attacks against `secure=True`:

```python run
from fastapi.testclient import TestClient

from pagebound import build_app

client = TestClient(build_app(secure=True))
ada, bo = {"Authorization": "Bearer t-ada"}, {"Authorization": "Bearer t-bo"}
root = {"Authorization": "Bearer t-root"}

print("ada reads own order 1 :", client.get("/orders/1", headers=ada).status_code)
print("ada reads bo's order 3:", client.get("/orders/3", headers=ada).status_code, client.get("/orders/3", headers=ada).json())
print("ada reads missing 999 :", client.get("/orders/999", headers=ada).status_code, "<- same answer as 'not yours'")
print("ada cancels bo's order:", client.post("/orders/3/cancel", headers=ada).status_code)
print("bo's order is still   :", client.get("/orders/3", headers=bo).json()["status"])
print("ada lists users       :", client.get("/admin/users", headers=ada).status_code)
print("admin lists users     :", client.get("/admin/users", headers=root).json()[0])
r = client.patch("/users/me", json={"name": "Ada", "role": "admin"}, headers=ada)
print("ada sets role=admin   :", r.status_code, r.json()["detail"][0]["type"], r.json()["detail"][0]["loc"])
print("ada renames herself   :", client.patch("/users/me", json={"name": "Ada L."}, headers=ada).json())
```
```text
ada reads own order 1 : 200
ada reads bo's order 3: 404 {'detail': 'order not found'}
ada reads missing 999 : 404 <- same answer as 'not yours'
ada cancels bo's order: 404
bo's order is still   : pending
ada lists users       : 403
admin lists users     : {'id': 1, 'name': 'ada', 'role': 'customer'}
ada sets role=admin   : 422 extra_forbidden ['body', 'role']
ada renames herself   : {'id': 1, 'name': 'Ada L.', 'role': 'customer'}
```

(The `extra_forbidden` error is Pydantic rejecting the unknown field `role`, the same machinery as swe.05 section 5.)

### 8.4 The two-actor test

A single logged-in user cannot reveal an IDOR bug: with one user, every object you fetch is yours. The test needs **two actors**:

1. **Arrange:** create a resource as user A.
2. **Act:** request it as user B (and as an anonymous caller).
3. **Assert:** the response is `404` (or `403`/`401`), the body contains none of A's data, and for write endpoints **A's data is unchanged afterwards**. Checking the side effect matters: a bug that returns `404` *after* performing the update would pass a status-only test.

```python run
from fastapi.testclient import TestClient

from pagebound import build_app

A, B, STAFF = {"Authorization": "Bearer t-ada"}, {"Authorization": "Bearer t-bo"}, {"Authorization": "Bearer t-sam"}


def check_isolation(secure: bool) -> list[str]:
    """Return a list of problems. An empty list means the rules hold."""
    c = TestClient(build_app(secure))
    problems = []

    # reading someone else's order
    for who, headers in (("another customer", B), ("anonymous", {})):
        r = c.get("/orders/1", headers=headers)
        if r.status_code not in (401, 404):
            problems.append(f"{who} got {r.status_code} reading order 1 (expected 401/404)")
        if "total_cents" in r.text:
            problems.append(f"{who} received order data in the body")

    # cancelling someone else's order must fail AND must not change anything
    r = c.post("/orders/1/cancel", headers=B)
    if r.status_code != 404:
        problems.append(f"another customer got {r.status_code} cancelling order 1")
    if c.get("/orders/1", headers=A).json()["status"] != "pending":
        problems.append("order 1 was cancelled by someone else (side effect!)")

    # function-level: a customer must not reach admin endpoints
    r = c.get("/admin/users", headers=A)
    if r.status_code != 403:
        problems.append(f"customer got {r.status_code} on /admin/users (expected 403)")
    elif "password_hash" in r.text:
        problems.append("password hashes leaked")

    # property-level: a customer cannot change their own role
    c.patch("/users/me", json={"role": "admin"}, headers=A)
    if c.get("/admin/users", headers=A).status_code != 403:
        problems.append("customer escalated to admin through PATCH /users/me")

    # the owner still works (a test that only checks denials passes for a server that denies everything)
    if c.get("/orders/1", headers=A).status_code != 200:
        problems.append("the owner can no longer read their own order")
    return problems


for secure in (False, True):
    found = check_isolation(secure)
    print(f"secure={secure}: {len(found)} problem(s)")
    for p in found:
        print("   -", p)
```
```text
secure=False: 6 problem(s)
   - another customer got 200 reading order 1 (expected 401/404)
   - another customer received order data in the body
   - another customer got 200 cancelling order 1
   - order 1 was cancelled by someone else (side effect!)
   - customer got 200 on /admin/users (expected 403)
   - customer escalated to admin through PATCH /users/me
secure=True: 0 problem(s)
```

This test **fails on the vulnerable app and passes on the fixed one**. Always run a new security test against the broken version once: a test that cannot fail proves nothing. Notice the last check too: a server that returns `404` for everything would pass every denial check, so we also assert that the legitimate owner still succeeds.

#### Make forgetting impossible: test every route

New endpoints are where IDOR returns. A **meta-test** lists the routes of the real app and fails when a route has no entry in your security test table:

```python run
from fastapi.routing import APIRoute

from pagebound import build_app

app = build_app(secure=True)
routes = {(m, r.path) for r in app.routes if isinstance(r, APIRoute) for m in r.methods}

# every route must be listed here, with the test that covers it, or be on the reviewed public list
covered = {
    ("GET", "/orders/{order_id}"): "object-level read",
    ("POST", "/orders/{order_id}/cancel"): "object-level write",
    ("GET", "/admin/users"): "function-level",
    ("PATCH", "/users/me"): "property-level",
}
print("routes in the app :", len(routes))
print("not covered       :", sorted(routes - set(covered)) or "none")
print("stale test entries:", sorted(set(covered) - routes) or "none")

app.add_api_route("/orders/{order_id}/refund", lambda order_id: {}, methods=["POST"])      # a developer adds a route...
routes = {(m, r.path) for r in app.routes if isinstance(r, APIRoute) for m in r.methods}
print("after a new route :", sorted(routes - set(covered)))
```
```text
routes in the app : 4
not covered       : none
stale test entries: none
after a new route : [('POST', '/orders/{order_id}/refund')]
```

In your real test-suite, make the second line an `assert`. The build then fails the day somebody adds `POST /orders/{order_id}/refund` without writing its two-actor test. That turns "remember to check ownership" from a habit into a rule that a machine enforces.

### 8.5 Related bugs in the same family

- **Function-level (BFLA):** the customer reaching `/admin/users`. Test every privileged route with a lower role and expect `403`.
- **Mass assignment:** accepting whatever fields arrive (`role`, `is_admin`, `owner_id`, `price`). Fix with separate *input* models listing exactly the writable fields, and `extra="forbid"` so extra fields are loud (swe.05 sections 4 and 7; swe.06 section 11.2).
- **Excessive data exposure:** returning a whole row or model and trusting the front end to hide fields (`password_hash`, internal notes, other users' e-mails). Use an explicit *output* model, and test that sensitive keys never appear.
- **Child objects:** `/orders/1/items/7` must check that item 7 belongs to order 1 **and** that order 1 belongs to the caller.
- **Search and list endpoints:** `GET /orders?owner_id=2` must not let a customer list another user's orders by passing a filter. Scope the base query first, and then apply the filters.
- **Bulk and export endpoints:** one forgotten filter exposes everything at once.

### Try it: fix this

```python
@app.delete("/notes/{note_id}")
def delete_note(note_id: int, user=Depends(current_user)):
    db.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    return {"deleted": note_id}
```

What is wrong, how do you fix it, and what test do you write?

<details><summary>Answer</summary>

Any logged-in user can delete any note (IDOR on a write). Fix: `DELETE FROM notes WHERE id = ? AND owner_id = ?`, check `cursor.rowcount`, and return `404` when it is `0`. Test with two actors: user A creates note 1; user B sends `DELETE /notes/1` and gets `404`; then A fetches note 1 and it still exists (the side-effect check); and A deleting their own note returns `200`/`204`. Run the test against the unfixed code once to see it fail.

</details>

### Try it: the 403 that leaks

An endpoint returns `403 "this order belongs to another user"` for other people's orders and `404` for ids that do not exist. What can an attacker do with that?

<details><summary>Answer</summary>

They can **enumerate** which order ids exist: `403` means real, `404` means not. That reveals how many orders the shop has, when they were created, and which ids to target in a second attack. Return `404` in both cases (section 7.5). The same applies to "user already registered" messages.

</details>

## 9. REST API design that is hard to misuse

Good API design is a security tool: a consistent, predictable API gives fewer places for a mistake to hide. This section is the practical core of REST (you saw the vocabulary in swe.02).

### 9.1 Resources, not actions

Think in **resources** (things with an identity) and use the HTTP method as the verb:

| Do | Avoid |
|---|---|
| `GET /orders` | `GET /getOrders` |
| `POST /orders` (create) | `POST /createOrder` |
| `GET /orders/42` | `GET /order?id=42` for the item |
| `PATCH /orders/42` (change fields) | `POST /updateOrder` |
| `DELETE /orders/42` | `GET /orders/42/delete` (a `GET` that changes state is a CSRF gift) |
| `GET /users/7/orders` (a sub-collection) | deep nesting like `/a/1/b/2/c/3/d/4` |

When something is truly an *action* rather than a field change ("cancel", "refund", "publish"), model it as a **sub-resource with POST**: `POST /orders/42/cancel`. It is explicit, permissioned separately, and easy to log. Use plural nouns, lowercase, hyphens in multi-word names, and keep the query string for **filters, sorting and paging** (`/orders?status=paid&sort=-created`), not for identifying the resource.

### 9.2 Method semantics: safe and idempotent

| Method | Safe (no change)? | Idempotent (same effect if repeated)? | Typical use |
|---|---|---|---|
| `GET`, `HEAD` | **yes** | yes | read |
| `PUT` | no | **yes** | replace a whole resource |
| `DELETE` | no | **yes** | remove |
| `PATCH` | no | not guaranteed | partial change |
| `POST` | no | **no** | create, or run an action |

Why care? Networks fail, so clients **retry**. Retrying a `GET`, `PUT` or `DELETE` is always safe: the end state is the same. Retrying a `POST` can do the thing twice (two orders, two charges). That single fact leads to section 13. Also, proxies, browsers and prefetchers are allowed to repeat or pre-load `GET`, so a `GET` that changes anything is a bug waiting to happen.

### 9.3 Status codes that mean something

| Code | Use for |
|---|---|
| **200** OK | success with a body |
| **201** Created | `POST` made something; send a `Location` header with its URL |
| **202** Accepted | accepted, work continues in the background |
| **204** No Content | success, nothing to return (usual for `DELETE`) |
| **400** Bad Request | malformed request (broken JSON) |
| **401** Unauthorized | missing or invalid credentials |
| **403** Forbidden | known caller, not permitted |
| **404** Not Found | no such resource (or hidden from you) |
| **405** Method Not Allowed | path exists, method does not |
| **409** Conflict | clashes with current state (duplicate, already cancelled, version mismatch) |
| **412** Precondition Failed | `If-Match` did not match (section 12) |
| **413** Content Too Large | body bigger than allowed |
| **415** Unsupported Media Type | wrong `Content-Type` |
| **422** Unprocessable Content | well-formed but invalid data (FastAPI validation) |
| **429** Too Many Requests | rate limited; send `Retry-After` |
| **500** / **502** / **503** | server error / bad upstream / unavailable |

### 9.4 One error format

Clients (and your own front end) cope much better when every error has the same shape. The standard for HTTP APIs is **problem details**, RFC 9457 (which replaced RFC 7807), with media type `application/problem+json`: `type`, `title`, `status`, `detail`, `instance`, plus fields you add. The second rule is safety: an error body must help the *client* and give the *attacker* nothing: no stack traces, SQL, file paths or "user not found" versus "wrong password".

```python run
import logging
import uuid

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from starlette.exceptions import HTTPException as StarletteHTTPException

logging.disable(logging.CRITICAL)                      # keep the demo output clean
app = FastAPI()


def problem(status: int, title: str, detail: str, request: Request, **extra):
    body = {"type": "about:blank", "title": title, "status": status, "detail": detail,
            "instance": request.url.path} | extra
    return JSONResponse(body, status_code=status, media_type="application/problem+json")


@app.exception_handler(StarletteHTTPException)
async def http_error(request: Request, exc: StarletteHTTPException):
    return problem(exc.status_code, "HTTP error", str(exc.detail), request)


@app.exception_handler(RequestValidationError)
async def validation_error(request: Request, exc: RequestValidationError):
    errors = [{"field": ".".join(str(p) for p in e["loc"][1:]), "message": e["msg"]} for e in exc.errors()]
    return problem(422, "Validation failed", "One or more fields are invalid.", request, errors=errors)


@app.exception_handler(Exception)
async def unexpected(request: Request, exc: Exception):
    incident = uuid.uuid4().hex[:8]
    logging.getLogger("app").exception("incident %s", incident)         # details go to the LOG...
    return problem(500, "Internal error", "Something went wrong.", request, incident=incident)   # ...not the client


@app.get("/orders/{order_id}")
def get_order(order_id: int):
    if order_id == 13:
        raise RuntimeError("password=hunter2 in connection string postgres://admin:hunter2@db/prod")
    raise HTTPException(404, "order not found")


client = TestClient(app, raise_server_exceptions=False)
for path in ("/orders/5", "/orders/abc", "/orders/13"):
    r = client.get(path)
    body = r.json()
    body.pop("incident", None)
    print(r.status_code, r.headers["content-type"], body)
print("secret leaked in a 500 body:", "hunter2" in client.get("/orders/13").text)
```
```text
404 application/problem+json {'type': 'about:blank', 'title': 'HTTP error', 'status': 404, 'detail': 'order not found', 'instance': '/orders/5'}
422 application/problem+json {'type': 'about:blank', 'title': 'Validation failed', 'status': 422, 'detail': 'One or more fields are invalid.', 'instance': '/orders/abc', 'errors': [{'field': 'order_id', 'message': 'Input should be a valid integer, unable to parse string as an integer'}]}
500 application/problem+json {'type': 'about:blank', 'title': 'Internal error', 'status': 500, 'detail': 'Something went wrong.', 'instance': '/orders/13'}
secret leaked in a 500 body: False
```

The 500 response gives the client a short `incident` id, and the full traceback goes to the log. When a user reports a problem, support searches the log for that id.

### 9.5 Design details that prevent bugs

- **Money:** never a float. `0.1 + 0.2` is `0.30000000000000004`. Send amounts as integer minor units (`"total_cents": 2500`) or as decimal strings, with a currency code.
- **Time:** ISO 8601 in UTC (`"2026-11-09T10:30:00Z"`), never local time without an offset.
- **Ids:** strings or integers, stable for ever, never reused. Do not expose database internals you may want to change.
- **Names and types:** one naming style (`snake_case`), the same field has the same name and type everywhere; enums as strings.
- **Create returns `201` + `Location` + the created object**, so the client does not need a second call.
- **Do not reflect or accept more than needed:** reject unknown fields, cap sizes, return only what the client needs.
- **Never secrets in URLs:** tokens in query strings get logged and cached.

```python run
from decimal import Decimal

print("float :", 0.1 + 0.2, "| ten times 0.10 =", sum([0.1] * 10))
print("cents :", 1999 * 3, "(integer arithmetic is exact)")
print("string:", Decimal("19.99") * 3)
```
```text
float : 0.30000000000000004 | ten times 0.10 = 1.0
cents : 5997 (integer arithmetic is exact)
string: 59.97
```

### Try it: status codes

Pick the best status for each: (a) `POST /orders` succeeded; (b) `DELETE /orders/42` succeeded, nothing to return; (c) the same email is already registered; (d) the JSON body has a syntax error; (e) the user is logged in but is not an admin.

<details><summary>Answer</summary>

(a) **201** with a `Location` header. (b) **204**. (c) **409** Conflict (or 422 if you treat it as a validation error; be consistent). (d) **400**. (e) **403**. A good answer also says why: 401 would wrongly suggest "log in again", and 200 for an error hides failures from monitoring and from clients.

</details>

## 10. Pagination, filtering and sorting

### 10.1 Never return an unbounded list

`GET /orders` that returns every order is a denial-of-service attack on your own database and a one-request data dump. **Every list endpoint needs a default page size, a maximum, and a stable order.** Reject `limit=1000000` rather than honouring it.

### 10.2 Offset pagination, and where it fails

The simple way is `?limit=20&offset=40` (`LIMIT 20 OFFSET 40`). It is easy and lets a client jump to page 7. It has two problems:

- **Slow for deep pages.** The database still reads and discards the first `offset` rows. Page 50,000 is far slower than page 1.
- **Unstable.** If rows are added or removed while the client is paging, items are repeated or skipped. Here a new order arrives between page 1 and page 2:

```python run
import sqlite3

db = sqlite3.connect(":memory:")
db.execute("CREATE TABLE orders (id INTEGER PRIMARY KEY, total INTEGER)")
db.executemany("INSERT INTO orders (total) VALUES (?)", [(i * 10,) for i in range(1, 7)])      # ids 1..6


def page_offset(offset, limit=3):
    return [r[0] for r in db.execute("SELECT id FROM orders ORDER BY id DESC LIMIT ? OFFSET ?", (limit, offset))]

page1 = page_offset(0)
db.execute("INSERT INTO orders (total) VALUES (999)")        # a new order arrives (id 7) while the client reads
page2 = page_offset(3)
print("page 1:", page1)
print("page 2:", page2, "<- order 4 appears again: the page boundary moved")
```
```text
page 1: [6, 5, 4]
page 2: [4, 3, 2] <- order 4 appears again: the page boundary moved
```

The newest-first list shifted down by one when row 7 appeared, so the client sees id `4` again. With deletions the opposite happens: rows are **skipped**, and a client syncing data silently loses records.

### 10.3 Keyset (cursor) pagination

Instead of "skip N rows", say "give me the rows **after this one**". The cursor is the sort key of the last row seen. The query uses an index and never scans skipped rows, and inserts cannot move the boundary:

```python run
import base64
import json
import sqlite3

db = sqlite3.connect(":memory:")
db.execute("CREATE TABLE orders (id INTEGER PRIMARY KEY, total INTEGER)")
db.executemany("INSERT INTO orders (total) VALUES (?)", [(i * 10,) for i in range(1, 7)])


def encode_cursor(last_id: int) -> str:
    return base64.urlsafe_b64encode(json.dumps({"id": last_id}).encode()).decode()


def decode_cursor(cursor: str) -> int:
    try:
        value = json.loads(base64.urlsafe_b64decode(cursor.encode()))["id"]
        if not isinstance(value, int):
            raise TypeError
        return value
    except (ValueError, KeyError, TypeError):
        raise ValueError("invalid cursor") from None


def page_after(cursor=None, limit=3):
    last = decode_cursor(cursor) if cursor else 10**18
    rows = db.execute("SELECT id FROM orders WHERE id < ? ORDER BY id DESC LIMIT ?", (last, limit + 1)).fetchall()
    ids = [r[0] for r in rows]
    has_more = len(ids) > limit                                    # we fetched one extra row to know
    items = ids[:limit]
    return {"items": items, "has_more": has_more, "next_cursor": encode_cursor(items[-1]) if has_more else None}


p1 = page_after()
db.execute("INSERT INTO orders (total) VALUES (999)")             # same interruption as before
p2 = page_after(p1["next_cursor"])
print("page 1:", p1["items"], "has_more:", p1["has_more"])
print("page 2:", p2["items"], "has_more:", p2["has_more"], "<- no repeats, no skips")
try:
    page_after("not-a-cursor")
except ValueError as exc:
    print("bad cursor:", exc)
```
```text
page 1: [6, 5, 4] has_more: True
page 2: [3, 2, 1] has_more: False <- no repeats, no skips
bad cursor: invalid cursor
```

Points to remember:

- The sort key must be **unique and stable**. Sorting by `created_at` alone can tie; use `(created_at, id)` and compare both: `WHERE (created_at, id) < (?, ?)` (SQLite and PostgreSQL support row values).
- **Fetch `limit + 1` rows** to learn whether there is a next page without a slow `COUNT(*)`.
- The cursor is **opaque** to clients (base64 of JSON here): they must not build it, so you can change it later. It is *input from the network*, so decode it defensively (above), and use the decoded values only as query parameters, never in SQL text. If the cursor encodes anything sensitive or you must stop clients forging it, sign it (HMAC, section 6.4).
- Keyset pagination cannot "jump to page 7", and a total count is expensive. For admin tables that need page numbers, offset with a modest maximum is fine; for feeds, syncing and large tables, use cursors.

### 10.4 Filtering and sorting: allow-lists only

Query parameters tempt developers to build SQL from them. Never interpolate a column name or a sort direction from the request into SQL text. Parameters (`?`) protect **values**, not identifiers. Map the user's words to your words:

```python run
import sqlite3

db = sqlite3.connect(":memory:")
db.execute("CREATE TABLE orders (id INTEGER PRIMARY KEY, total_cents INTEGER, status TEXT, secret_note TEXT)")
db.executemany("INSERT INTO orders (total_cents, status, secret_note) VALUES (?,?,?)",
               [(2500, "paid", "vip"), (990, "pending", "x"), (4200, "paid", "y")])

SORTABLE = {"total": "total_cents", "id": "id"}                         # public name -> column
FILTERABLE = {"status": {"paid", "pending", "cancelled"}}                # field -> allowed values


def list_orders(sort="id", status=None):
    descending = sort.startswith("-")
    column = SORTABLE.get(sort.lstrip("-"))
    if column is None:
        raise ValueError(f"cannot sort by {sort!r}; allowed: {sorted(SORTABLE)}")
    sql, args = "SELECT id, total_cents, status FROM orders", []         # note: secret_note is never selected
    if status is not None:
        if status not in FILTERABLE["status"]:
            raise ValueError("invalid status")
        sql += " WHERE status = ?"
        args.append(status)
    sql += f" ORDER BY {column} {'DESC' if descending else 'ASC'}"       # both parts come from OUR constants
    return db.execute(sql, args).fetchall()


print(list_orders(sort="-total", status="paid"))
for evil in ("id; DROP TABLE orders", "secret_note", "(SELECT secret_note FROM orders LIMIT 1)"):
    try:
        list_orders(sort=evil)
    except ValueError as exc:
        print("refused:", evil[:30])
```
```text
[(3, 4200, 'paid'), (1, 2500, 'paid')]
refused: id; DROP TABLE orders
refused: secret_note
refused: (SELECT secret_note FROM order
```

Two further rules for filters:

- **Do not allow filtering or sorting on fields users may not read.** If `?password_hash__startswith=a` or `?sort=secret_note` is accepted, an attacker reads the hidden field one character at a time from the *order of results* (a "filter oracle"). Frameworks that expose every column to filters (`django-filter`'s `fields = "__all__"`, GraphQL auto-filters) need an explicit allow-list.
- **Scope first, filter second.** The base query is "orders of this user"; the filters narrow it. Never let a filter parameter (`?owner_id=2`) widen it.

### 10.5 A paginated endpoint with validated parameters

```python run
import sqlite3

from fastapi import FastAPI, Header, HTTPException, Query
from fastapi.testclient import TestClient

db = sqlite3.connect(":memory:", check_same_thread=False)
db.execute("CREATE TABLE orders (id INTEGER PRIMARY KEY, owner_id INTEGER, total_cents INTEGER)")
db.executemany("INSERT INTO orders (owner_id, total_cents) VALUES (?,?)", [(2 - i % 2, 100 * i) for i in range(1, 11)])
USERS = {"t-ada": 1, "t-bo": 2}
app = FastAPI()


@app.get("/orders")
def list_orders(authorization: str = Header(default=""), limit: int = Query(3, ge=1, le=50),
                before_id: int | None = Query(None, ge=1)):
    owner = USERS.get(authorization.removeprefix("Bearer "))
    if owner is None:
        raise HTTPException(401, "login required")
    rows = db.execute("SELECT id, total_cents FROM orders WHERE owner_id = ? AND id < ? ORDER BY id DESC LIMIT ?",
                      (owner, before_id or 10**18, limit + 1)).fetchall()      # scope first, then page
    items = [{"id": r[0], "total_cents": r[1]} for r in rows[:limit]]
    return {"items": items, "next_before_id": items[-1]["id"] if len(rows) > limit else None}


c = TestClient(app)
ada = {"Authorization": "Bearer t-ada"}
page1 = c.get("/orders", headers=ada).json()
print("page 1:", [i["id"] for i in page1["items"]], "next:", page1["next_before_id"])
page2 = c.get("/orders", headers=ada, params={"before_id": page1["next_before_id"]}).json()
print("page 2:", [i["id"] for i in page2["items"]], "next:", page2["next_before_id"])
print("limit=1000 :", c.get("/orders", headers=ada, params={"limit": 1000}).status_code)
print("limit=0    :", c.get("/orders", headers=ada, params={"limit": 0}).status_code)
print("all pages only contain ada's (odd) ids:", all(i["id"] % 2 == 1 for p in (page1, page2) for i in p["items"]))
```
```text
page 1: [9, 7, 5] next: 5
page 2: [3, 1] next: None
limit=1000 : 422
limit=0    : 422
all pages only contain ada's (odd) ids: True
```

### Try it: when offset is fine

Name one case where you would still choose offset pagination, and one where you must not.

<details><summary>Answer</summary>

Fine: a small admin table (hundreds of rows) where staff want page numbers and "jump to page 7"; a hard maximum offset keeps it cheap. Must not: a public feed or an export/sync API over a large, changing table: offsets get slow with depth and drift while rows are inserted or deleted, so clients repeat or lose records. Use keyset cursors there.

</details>

### Try it: the sort oracle

A search endpoint accepts `?sort=<any column>`. The users table has `password_hash` and the endpoint only returns `id` and `name`. How can an attacker still learn hash prefixes, and what is the fix?

<details><summary>Answer</summary>

By sorting on `password_hash` and observing the order of the returned ids, they can infer information about the hashes (and with a filter such as `password_hash LIKE 'a%'` even more). The fix is an allow-list of sortable and filterable fields (section 10.4) that contains only fields the caller is allowed to read.

</details>


## 11. Rate limiting and abuse protection

### 11.1 Why limit anything?

Without limits, one client can use all your capacity. Rate limiting protects against:

- **Brute force and credential stuffing** on login and password-reset endpoints.
- **Scraping** and bulk data extraction.
- **Accidental floods**: a buggy client in an infinite retry loop.
- **Cost and fairness**: an expensive endpoint (report, search, e-mail sending) used by one tenant should not starve the others.
- **Denial of service** at the application layer.

Limits live in **layers**. A CDN, WAF, reverse proxy (nginx `limit_req`) or API gateway stops floods before they reach Python. Your **application** adds the limits only it can know: per user, per API key, per plan, per endpoint ("5 reports per minute"). Use both.

### 11.2 Four algorithms, one scenario

All limiters answer "may this request pass now?". They differ in how they count. The clock is **passed in**, so tests never sleep:

```python
# limiters.py
from collections import deque


class FixedWindow:
    """Count requests in each clock-aligned window (e.g. seconds 0-10, 10-20)."""
    def __init__(self, limit, window, now):
        self.limit, self.window, self.now = limit, window, now
        self.slot, self.count = None, 0

    def allow(self):
        slot = int(self.now() // self.window)
        if slot != self.slot:
            self.slot, self.count = slot, 0
        if self.count < self.limit:
            self.count += 1
            return True
        return False


class SlidingWindowLog:
    """Remember the time of every recent request. Exact, but uses memory proportional to the limit."""
    def __init__(self, limit, window, now):
        self.limit, self.window, self.now = limit, window, now
        self.times = deque()

    def allow(self):
        t = self.now()
        while self.times and self.times[0] <= t - self.window:
            self.times.popleft()
        if len(self.times) < self.limit:
            self.times.append(t)
            return True
        return False


class TokenBucket:
    """A bucket of `capacity` tokens refilled at `rate` per second; each request takes one."""
    def __init__(self, capacity, rate, now):
        self.capacity, self.rate, self.now = capacity, rate, now
        self.tokens, self.last = float(capacity), now()

    def allow(self, cost=1):
        t = self.now()
        self.tokens = min(self.capacity, self.tokens + (t - self.last) * self.rate)
        self.last = t
        if self.tokens >= cost:
            self.tokens -= cost
            return True
        return False

    def retry_after(self, cost=1):
        """Seconds until `cost` tokens are available (0 if available now)."""
        missing = cost - self.tokens
        return 0.0 if missing <= 0 else missing / self.rate
```

The scenario: **5 requests per 10 seconds**. A client sends 5 requests at second 9.9 and another 5 at second 10.1, 0.2 seconds later:

```python run
from limiters import FixedWindow, SlidingWindowLog, TokenBucket

clock = [0.0]
now = lambda: clock[0]
limiters = {
    "fixed window": FixedWindow(5, 10, now),
    "sliding log": SlidingWindowLog(5, 10, now),
    "token bucket": TokenBucket(capacity=5, rate=0.5, now=now),       # 0.5/s = 5 per 10 s sustained
}
for name, lim in limiters.items():
    clock[0] = 9.9
    first = sum(lim.allow() for _ in range(5))
    clock[0] = 10.1
    second = sum(lim.allow() for _ in range(5))
    print(f"{name:13} burst at 9.9s: {first} allowed | burst at 10.1s: {second} allowed | total in 0.2 s: {first + second}")
```
```text
fixed window  burst at 9.9s: 5 allowed | burst at 10.1s: 5 allowed | total in 0.2 s: 10
sliding log   burst at 9.9s: 5 allowed | burst at 10.1s: 0 allowed | total in 0.2 s: 5
token bucket  burst at 9.9s: 5 allowed | burst at 10.1s: 0 allowed | total in 0.2 s: 5
```

Study the result:

| Algorithm | Behaviour | Cost | Weakness |
|---|---|---|---|
| **Fixed window** | counter that resets at window edges | tiny: one counter | allows **double** the limit around a boundary (10 requests in 0.2 s, shown above) |
| **Sliding window log** | exact count over "the last 10 seconds" | memory per request | storage for high limits |
| **Token bucket** | refills steadily; allows bursts up to the capacity, then the sustained rate | two numbers | you tune capacity (burst) and rate (average) separately |

The token bucket is the most common choice for APIs because it models what you want: a normal short burst is fine (a page load makes 8 calls), a sustained flood is not. A *leaky bucket* is its smoothing cousin (it releases requests at a constant rate), and a *sliding window counter* approximates the log with two counters.

### 11.3 What to key the limit on

| Key | Good for | Careful about |
|---|---|---|
| **IP address** | anonymous traffic, login attempts | many users share one IP (offices, mobile carriers); attackers rotate IPs; behind a proxy every request seems to come from the proxy |
| **User id** | logged-in traffic | does not stop an attacker who creates many accounts |
| **API key** | customers and plans | a leaked key is limited as well, which helps |
| **Route** | stricter limits on `/login`, `/password-reset`, `/reports` | |
| **Combination** | login: `(username, IP)` | |

**Trust the client IP only from your own proxy.** The `X-Forwarded-For` header is written by whoever sends the request; an attacker can set it to any value and get a fresh rate-limit bucket each time. Configure your server (Uvicorn's `--forwarded-allow-ips`, nginx's `real_ip` module) to read it only from known proxies, and use the address your server derives, not the raw header.

### 11.4 Telling the client: 429 and Retry-After

A refusal is `429 Too Many Requests`. Add `Retry-After: <seconds>` so well-behaved clients wait instead of hammering. Many APIs also publish their limits in headers (`X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`; an IETF draft is standardising `RateLimit` header fields). Here is a reusable FastAPI dependency using a token bucket per key, tested with a fake clock:

```python run
import math

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.testclient import TestClient

from limiters import TokenBucket

clock = [0.0]
now = lambda: clock[0]


def rate_limit(capacity: int, rate: float, scope: str):
    buckets: dict[str, TokenBucket] = {}

    def dependency(request: Request, response: Response):
        key = f"{scope}:{request.client.host}"                    # in real life: user id or API key when known
        bucket = buckets.setdefault(key, TokenBucket(capacity, rate, now))
        if not bucket.allow():
            wait = math.ceil(bucket.retry_after())
            raise HTTPException(429, "rate limit exceeded", headers={"Retry-After": str(wait)})
        response.headers["X-RateLimit-Remaining"] = str(int(bucket.tokens))
    return dependency


app = FastAPI()


@app.post("/login", dependencies=[Depends(rate_limit(capacity=5, rate=5 / 60, scope="login"))])
def login():
    return {"ok": False}                                           # pretend every attempt fails


@app.get("/orders", dependencies=[Depends(rate_limit(capacity=100, rate=10, scope="orders"))])
def orders():
    return []


c = TestClient(app)
codes = [c.post("/login").status_code for _ in range(7)]
print("7 quick login attempts:", codes)
blocked = c.post("/login")
print("blocked response      :", blocked.status_code, "Retry-After:", blocked.headers["retry-after"], "s")
clock[0] += 12.0                                                   # twelve seconds later (one token = 12 s)
print("after waiting 12 s    :", c.post("/login").status_code)
print("other route unaffected:", c.get("/orders").status_code, "| remaining:", c.get("/orders").headers["x-ratelimit-remaining"])
```
```text
7 quick login attempts: [200, 200, 200, 200, 200, 429, 429]
blocked response      : 429 Retry-After: 12 s
after waiting 12 s    : 200
other route unaffected: 200 | remaining: 98
```

Notice that each route has its **own** bucket (`scope`), and login is far stricter (5 per minute) than reading orders. The same `Retry-After` value tells a polite client exactly how long to wait.

### 11.5 Login protection: throttle, do not lock

A tempting rule is "lock the account after 5 wrong passwords". It has a nasty side effect: an attacker can lock **any** user out just by sending wrong passwords, which is a denial of service on your customers. Better:

- **Progressive delay** or a per-`(username, IP)` token bucket, as above.
- A **global** budget on failures per username, which triggers extra proof (CAPTCHA, an e-mail challenge, MFA) rather than a hard lock.
- Alert on spikes of failed logins, and check new passwords against known-breached lists (section 2.4).
- Remember that **slow hashing** (section 2) already makes each guess cost something; rate limiting stops the *volume*.

### 11.6 Several workers, several servers

An in-memory dictionary, as above, counts per **process**. Run 4 workers and each has its own bucket, so the real limit is 4 times higher, and after a restart everybody starts fresh. For real deployments the counters live in a **shared store**: Redis with `INCR` plus `EXPIRE` for windows, or a small Lua script for token buckets (swe.08), or the rate-limit feature of your gateway. Test the logic with an in-memory fake (as here), and test the shared version separately.

> **Try it on your machine** (needs a Redis server, not available in this course environment):
>
> ```bash
> pip install redis
> python -c "import redis; r = redis.Redis(); k = 'rl:login:127.0.0.1'; n = r.incr(k); r.expire(k, 60) if n == 1 else None; print(n)"
> ```
>
> Run it several times within a minute: it prints `1`, `2`, `3`, ..., and the counter disappears 60 seconds after the first call. That is the fixed-window algorithm in two Redis commands. In production you would wrap them in a transaction or script so that the `EXPIRE` cannot be skipped.

### 11.7 Other limits that belong with rate limiting

| Limit | Why | Typical status |
|---|---|---|
| **Maximum request body** (say 1 MB, larger on upload routes) | memory and CPU | `413` |
| **Maximum page size** | data dumps | `422` or clamp (section 10) |
| **Timeouts** on outgoing calls and database queries | a slow dependency should not hold workers forever | `504`/`503` |
| **Concurrency limit** per user or expensive route | heavy reports | `429`/`503` |
| **Depth and size of JSON** (list lengths, nesting) | parser and validation cost | `422` |
| **Upload limits** and file count | disk | `413` |

A framework does not enforce a body limit for you. Reject on `Content-Length` early, and cap the bytes you actually read, because a client can lie or send chunks without a length:

```python run
from fastapi import FastAPI, HTTPException, Request
from fastapi.testclient import TestClient

MAX_BODY = 1_000                                                   # bytes, small for the demo
app = FastAPI()


@app.post("/import")
async def import_data(request: Request):
    declared = request.headers.get("content-length")
    if declared and int(declared) > MAX_BODY:
        raise HTTPException(413, "body too large")
    received = bytearray()
    async for chunk in request.stream():                           # never read more than the limit allows
        received += chunk
        if len(received) > MAX_BODY:
            raise HTTPException(413, "body too large")
    return {"bytes": len(received)}


c = TestClient(app)
print("500 bytes  :", c.post("/import", content=b"x" * 500).status_code)
print("5000 bytes :", c.post("/import", content=b"x" * 5000).status_code)
def chunks():                                                      # no Content-Length header: chunked upload
    for _ in range(10):
        yield b"x" * 500
print("chunked 5k :", c.post("/import", content=chunks()).status_code)
```
```text
500 bytes  : 200
5000 bytes : 413
chunked 5k : 413
```

In production the first line of defence is the reverse proxy (`client_max_body_size` in nginx), with the check above as a second layer.

### Try it: the boundary burst

A limiter allows 100 requests per minute using a fixed window. How many requests can pass in two seconds, in the worst case, and which algorithm fixes it?

<details><summary>Answer</summary>

200: 100 requests in the last second of one window and 100 in the first second of the next. A sliding window log or a token bucket (capacity 100, refill 100/60 per second) limits any 60-second period, not just clock-aligned ones. A token bucket would allow a burst of up to the capacity, then only the sustained rate, so choose the capacity to match the largest legitimate burst.

</details>

### Try it: the spoofed header

Your limiter keys on `request.headers["x-forwarded-for"]`. How does an attacker defeat it, and what do you change?

<details><summary>Answer</summary>

They send a different random `X-Forwarded-For` value with every request; each gets a fresh bucket, so the limit never triggers. Use the IP address your server sees on the connection (`request.client.host`), and where a trusted proxy sits in front, configure the server to take the forwarded address only from that proxy's IP.

</details>

## 12. Evolving an API: versions, deprecation and concurrent edits

### 12.1 Breaking and non-breaking changes

You cannot update every client at once: mobile apps stay installed for years, and partners release on their own schedule. So a change is either safe or it needs a new version.

| Usually **non-breaking** | **Breaking** |
|---|---|
| a new endpoint | removing or renaming a field |
| a new optional request field | changing a field's type or meaning (`total` from euros to cents) |
| a new field in a response | making an optional field required |
| a new optional query parameter | stricter validation of input that used to pass |
| | changing a status code or the error shape |
| | adding a new value to an enum clients switch on (clients may crash on unknown values) |

The matching rule for **clients**: ignore response fields you do not know. If every client does that, adding fields is always safe. State this rule in your API documentation.

### 12.2 Ways to version

| Strategy | Example | Notes |
|---|---|---|
| **URL path** | `/v1/orders`, `/v2/orders` | simplest, visible in logs and caches, easy to route; the common choice |
| **Header** | `API-Version: 2` or `Accept: application/vnd.pagebound.v2+json` | cleaner URLs, harder to try in a browser, easy to forget |
| **Query parameter** | `/orders?version=2` | avoid; mixes versioning with filtering |
| **Date-based** | `Pagebound-Version: 2026-11-01` (Stripe-style) | fine-grained, needs good tooling |

A sensible default: a **major version in the URL** (`/v1`), **additive changes inside a version**, and as few live versions as possible. Version the *API contract*, not every release of your code.

### 12.3 Two versions, one implementation

Keep the business logic and the security checks in one place and let each version only change the **shape** of the data:

```python run
from fastapi import APIRouter, FastAPI
from fastapi.testclient import TestClient

ORDERS = {7: {"id": 7, "total_cents": 2599, "currency": "EUR", "status": "paid"}}


def load_order(order_id: int) -> dict:                      # the ONE place with the logic (and the ownership check)
    return ORDERS[order_id]


v1, v2 = APIRouter(prefix="/v1"), APIRouter(prefix="/v2")


@v1.get("/orders/{order_id}")
def order_v1(order_id: int):
    o = load_order(order_id)
    return {"id": o["id"], "total": o["total_cents"] / 100, "status": o["status"]}        # old shape: float euros


@v2.get("/orders/{order_id}")
def order_v2(order_id: int):
    o = load_order(order_id)
    return {"id": o["id"], "total_cents": o["total_cents"], "currency": o["currency"], "status": o["status"]}


app = FastAPI()
app.include_router(v1)
app.include_router(v2)
c = TestClient(app)
print("v1:", c.get("/v1/orders/7").json())
print("v2:", c.get("/v2/orders/7").json())

# a contract test: old clients depend on exactly these keys, so a change to them must break the build
assert set(c.get("/v1/orders/7").json()) == {"id", "total", "status"}, "v1 contract changed!"
print("v1 contract holds")
```
```text
v1: {'id': 7, 'total': 25.99, 'status': 'paid'}
v2: {'id': 7, 'total_cents': 2599, 'currency': 'EUR', 'status': 'paid'}
v1 contract holds
```

The contract test is cheap protection: it fails if someone "tidies up" the v1 response. (Tools like schemathesis and OpenAPI diffing do this at scale.)

### 12.4 Deprecating and removing a version

1. Announce a date, in the documentation and e-mail.
2. Add machine-readable headers to responses of the old version: `Deprecation: true` (or a date), `Sunset: <HTTP date>` (RFC 8594), and `Link: <https://api.example/v2/orders>; rel="successor-version"`.
3. **Measure usage per version and client** in your logs; contact the stragglers.
4. After the sunset date return `410 Gone` for a while, and then remove the code.

```python run
from fastapi import FastAPI, Request, Response
from fastapi.testclient import TestClient

app = FastAPI()


@app.middleware("http")
async def deprecate_v1(request: Request, call_next):
    response: Response = await call_next(request)
    if request.url.path.startswith("/v1/"):
        response.headers["Deprecation"] = "true"
        response.headers["Sunset"] = "Sat, 31 Oct 2026 23:59:59 GMT"
        response.headers["Link"] = '</v2' + request.url.path[3:] + '>; rel="successor-version"'
    return response


@app.get("/v1/ping")
def ping():
    return {"ok": True}


r = TestClient(app).get("/v1/ping")
print({k: v for k, v in r.headers.items() if k in {"deprecation", "sunset", "link"}})
```
```text
{'deprecation': 'true', 'sunset': 'Sat, 31 Oct 2026 23:59:59 GMT', 'link': '</v2/ping>; rel="successor-version"'}
```

### 12.5 The security side of versions

Old versions are where forgotten bugs live. When a vulnerability is fixed in `/v2`, check `/v1` too: attackers love the "legacy" endpoint that still lacks the ownership check. Rules: all versions call the **same** authorisation code (as `load_order` above); keep an **inventory** of every deployed version and route (OWASP calls missing inventories "improper inventory management": forgotten `/v0`, `/debug`, `/internal` and staging hosts that stay online); and retire what you no longer support.

### 12.6 Lost updates: ETag and `If-Match`

Versioning is about the contract. A second evolution problem is **concurrent edits**. Two staff members open the same order, both change the note, both save. The second save silently overwrites the first (a *lost update*). The HTTP answer is **optimistic concurrency** with an `ETag`:

1. `GET` returns an `ETag` header, an opaque version label of the resource.
2. To change it, the client sends `If-Match: <that etag>`.
3. If the resource changed in between, the server answers **`412 Precondition Failed`**, and the client must reload and merge. If the header is missing on a resource that requires it, answer `428 Precondition Required`.

The server can keep a `version` integer per row and make the check part of the SQL, so it is atomic:

```python run
import sqlite3

from fastapi import FastAPI, Header, HTTPException, Response
from fastapi.testclient import TestClient
from pydantic import BaseModel

db = sqlite3.connect(":memory:", check_same_thread=False)
db.row_factory = sqlite3.Row
db.execute("CREATE TABLE orders (id INTEGER PRIMARY KEY, note TEXT, version INTEGER NOT NULL DEFAULT 1)")
db.execute("INSERT INTO orders (id, note) VALUES (1, 'original')")
app = FastAPI()


class NoteUpdate(BaseModel):
    note: str


@app.get("/orders/{order_id}")
def get_order(order_id: int, response: Response):
    row = db.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
    if row is None:
        raise HTTPException(404)
    response.headers["ETag"] = f'"{row["version"]}"'
    return dict(row)


@app.patch("/orders/{order_id}")
def patch_order(order_id: int, body: NoteUpdate, response: Response, if_match: str | None = Header(default=None)):
    if if_match is None:
        raise HTTPException(428, "send If-Match with the ETag you last read")
    cur = db.execute("UPDATE orders SET note = ?, version = version + 1 WHERE id = ? AND version = ?",
                     (body.note, order_id, int(if_match.strip('"'))))          # check and write in ONE statement
    db.commit()
    if cur.rowcount == 0:
        raise HTTPException(412, "the order changed; reload and try again")
    response.headers["ETag"] = f'"{int(if_match.strip(chr(34))) + 1}"'
    return {"ok": True}


c = TestClient(app)
alice = c.get("/orders/1").headers["etag"]                    # both clients read version 1
bob = c.get("/orders/1").headers["etag"]
print("alice saves :", c.patch("/orders/1", json={"note": "alice was here"}, headers={"If-Match": alice}).status_code)
print("bob saves   :", c.patch("/orders/1", json={"note": "bob was here"}, headers={"If-Match": bob}).status_code, "<- stale, refused")
print("no header   :", c.patch("/orders/1", json={"note": "x"}).status_code)
fresh = c.get("/orders/1")
print("bob reloads :", fresh.json()["note"], "| etag", fresh.headers["etag"])
print("bob retries :", c.patch("/orders/1", json={"note": "alice was here + bob"}, headers={"If-Match": fresh.headers["etag"]}).status_code)
```
```text
alice saves : 200
bob saves   : 412 <- stale, refused
no header   : 428
bob reloads : alice was here | etag "2"
bob retries : 200
```

The key detail is `WHERE id = ? AND version = ?` in a single `UPDATE`: reading the version in Python and then updating would leave a gap in which another request could sneak in. The same idea protects stock counts, balances and anything else with "read, think, write" logic. Section 13 applies the same care to repeated requests.

### Try it: breaking or not?

Classify each change as breaking or non-breaking for existing clients: (a) add `"estimated_delivery"` to the order response; (b) rename `"status"` to `"state"`; (c) add the value `"refunded"` to the `status` enum; (d) reject empty `note` strings that used to be accepted; (e) change the 404 body from `{"detail": ...}` to a problem-details object.

<details><summary>Answer</summary>

(a) non-breaking, if clients ignore unknown fields. (b) breaking. (c) potentially breaking: a client with a `switch` on the known values may crash or misbehave; document that enums can grow, or version it. (d) breaking: requests that worked now fail. (e) breaking for clients that parse the error body. A new major version, or an opt-in header, is the usual way to ship (b), (d) and (e).

</details>

### Try it: why not read, then write?

What goes wrong with this code, and what is the one-line fix?

```python
row = db.execute("SELECT version FROM orders WHERE id=?", (id,)).fetchone()
if row["version"] != client_version:
    raise HTTPException(412)
db.execute("UPDATE orders SET note=?, version=version+1 WHERE id=?", (note, id))
```

<details><summary>Answer</summary>

Between the `SELECT` and the `UPDATE`, another request can commit a change (a **race condition**), and both pass the check. The fix is to put the version check inside the `UPDATE` (`WHERE id=? AND version=?`) and test `rowcount`, so the database performs check-and-write as one atomic step.

</details>


## 13. Idempotency keys: a payment endpoint that is safe to call twice

This section delivers the second outcome of the chapter: **make a payment-style endpoint safe to call twice.**

### 13.1 The problem: you cannot tell "failed" from "succeeded but I did not hear"

A client sends `POST /payments` with 10.00 EUR. The server charges the account and writes the reply, but the network drops the reply. The client sees a timeout. Did the payment happen? It cannot know. If it gives up, the customer may have paid for nothing; if it **retries**, the customer may pay twice. Retrying is the right instinct (networks do fail, load balancers retry, users double-click, queues redeliver), so the *server* must make retries harmless.

Here is the naive endpoint and a client that loses the first response:

```python
# payments.py
import hashlib
import json
import sqlite3
import time

SCHEMA = """
CREATE TABLE accounts (user_id INTEGER PRIMARY KEY, balance_cents INTEGER NOT NULL CHECK (balance_cents >= 0));
CREATE TABLE payments (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL,
                       amount_cents INTEGER NOT NULL CHECK (amount_cents > 0));
CREATE TABLE idempotency (
    user_id INTEGER NOT NULL, key TEXT NOT NULL, fingerprint TEXT NOT NULL, status TEXT NOT NULL,
    locked_at REAL NOT NULL, response_code INTEGER, response_body TEXT,
    PRIMARY KEY (user_id, key)                      -- the database enforces "one row per key"
);
"""


def connect(path: str) -> sqlite3.Connection:
    db = sqlite3.connect(path, timeout=10, isolation_level=None)     # autocommit: we write BEGIN/COMMIT ourselves
    db.row_factory = sqlite3.Row
    return db


def init_db(path: str, balances: dict[int, int]) -> None:
    db = connect(path)
    db.executescript(SCHEMA)
    db.executemany("INSERT INTO accounts VALUES (?, ?)", balances.items())


def naive_create_payment(path: str, user_id: int, amount_cents: int):
    """No protection against repeats."""
    db = connect(path)
    cur = db.execute("UPDATE accounts SET balance_cents = balance_cents - ? WHERE user_id = ? AND balance_cents >= ?",
                     (amount_cents, user_id, amount_cents))
    if cur.rowcount == 0:
        return 402, {"detail": "insufficient funds"}
    payment_id = db.execute("INSERT INTO payments (user_id, amount_cents) VALUES (?, ?)", (user_id, amount_cents)).lastrowid
    return 201, {"payment_id": payment_id, "amount_cents": amount_cents}


def fingerprint_of(body: dict) -> str:
    """A hash of the request body, to notice when a key is reused for a different request."""
    return hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def balance(path: str, user_id: int) -> int:
    return connect(path).execute("SELECT balance_cents FROM accounts WHERE user_id = ?", (user_id,)).fetchone()[0]


def payment_count(path: str, user_id: int) -> int:
    return connect(path).execute("SELECT COUNT(*) FROM payments WHERE user_id = ?", (user_id,)).fetchone()[0]
```

```python run
import os
import tempfile

import payments as p

with tempfile.TemporaryDirectory() as tmp:
    path = os.path.join(tmp, "shop.db")
    p.init_db(path, {1: 10_000})                       # the customer has 100.00

    for attempt in (1, 2):
        status, body = p.naive_create_payment(path, user_id=1, amount_cents=2_500)
        if attempt == 1:
            continue                                   # the response was lost; the client saw only a timeout, so it retries
        print("client finally saw:", status, body)

    print("payments recorded :", p.payment_count(path, 1))
    print("balance           :", p.balance(path, 1), "(expected 7500)")
```
```text
client finally saw: 201 {'payment_id': 2, 'amount_cents': 2500}
payments recorded : 2
balance           : 5000 (expected 7500)
```

The customer paid 25.00 twice. The server did exactly what it was asked, twice. No amount of "be careful in the client" fixes this, because the client cannot know.

### 13.2 First choice: make the operation naturally idempotent

Before adding machinery, see if the design can make a repeat harmless:

- **`PUT` with a client-chosen id**: `PUT /payments/3f2a...` (the id is a UUID the client generated). Doing it twice writes the same row. The database's primary key does the work.
- **A unique constraint on the business fact**: "one payment per order" is `UNIQUE (order_id)`. The second attempt fails with a duplicate error, which you map to "already paid" and return the original result.
- **State machines**: cancelling an order that is already cancelled returns the same `200`, not an error. Setting a status to a value it already has is naturally idempotent.
- **Absolute, not relative, updates**: "set balance to X" is idempotent; "subtract 25" is not. (Money needs relative updates, so for those use a key.)

When none of these apply, as with "create a charge" and "send an e-mail", use an **idempotency key**.

### 13.3 The idempotency-key protocol

The client generates a unique key (a UUID) for each *logical operation* and sends it in a header: `Idempotency-Key: 8e03978e-40d5-43e8-bc93-6894a57f9324`. The same key is sent on **every retry of that operation**. A new operation gets a new key. The server rules:

| Situation when a request arrives | What the server does |
|---|---|
| key never seen | **claim it**, run the operation, store the response, reply |
| key seen, finished, **same request** | return the **stored response** (same status and body), do not run again; mark it `Idempotent-Replayed: true` |
| key seen, finished, **different request** (other amount) | refuse: `422`. A reused key with a new payload is a client bug |
| key seen, **still running** | `409 Conflict` with `Retry-After`; the client retries a moment later |
| key seen, "running" for a very long time | the first attempt probably crashed; allow a takeover after a timeout |

Four design points matter:

1. **Scope keys to the user** (`PRIMARY KEY (user_id, key)`). Otherwise one customer could guess or collide with another's key, and read their stored response.
2. **Claim the key before doing the work, using a unique constraint.** Two simultaneous requests with the same key race to `INSERT`; the database lets exactly one win. A "check then insert" in Python would let both through.
3. **Store a fingerprint of the request** (a hash of the body) to detect misuse.
4. **Make the work and the "completed" mark one transaction.** If the process dies after debiting but before recording, the transaction rolls back, nothing happened, and a retry is safe. For side effects outside your database (a card network, an e-mail), pass your key along as *their* idempotency key.

### 13.4 Implementation

```python
# payments_safe.py
import json
import sqlite3
import time

from payments import connect, fingerprint_of

LOCK_TIMEOUT = 30.0                                     # seconds before an "in_progress" claim is considered dead


def create_payment(path: str, user_id: int, key: str, body: dict, *, now=time.time, crash_after_debit=False):
    """Return (status_code, response_body, replayed). Safe to call any number of times with the same key."""
    db = connect(path)
    fp = fingerprint_of(body)
    t = now()

    # 1. claim the key; the PRIMARY KEY makes exactly one concurrent caller win
    try:
        db.execute("INSERT INTO idempotency (user_id, key, fingerprint, status, locked_at) VALUES (?, ?, ?, 'in_progress', ?)",
                   (user_id, key, fp, t))
    except sqlite3.IntegrityError:
        row = db.execute("SELECT * FROM idempotency WHERE user_id = ? AND key = ?", (user_id, key)).fetchone()
        if row is None:
            return 409, {"detail": "please retry"}, False            # deleted between our two statements
        if row["fingerprint"] != fp:
            return 422, {"detail": "this Idempotency-Key was already used with a different request"}, False
        if row["status"] == "completed":
            return row["response_code"], json.loads(row["response_body"]), True
        if t - row["locked_at"] < LOCK_TIMEOUT:
            return 409, {"detail": "a request with this key is still being processed"}, False
        taken = db.execute("UPDATE idempotency SET locked_at = ? WHERE user_id = ? AND key = ? AND status = 'in_progress' "
                           "AND locked_at = ?", (t, user_id, key, row["locked_at"]))    # take over a dead claim, once
        if taken.rowcount != 1:
            return 409, {"detail": "a request with this key is still being processed"}, False

    # 2. do the work and record the result in ONE transaction
    amount = body["amount_cents"]
    try:
        db.execute("BEGIN IMMEDIATE")
        cur = db.execute("UPDATE accounts SET balance_cents = balance_cents - ? WHERE user_id = ? AND balance_cents >= ?",
                         (amount, user_id, amount))
        if cur.rowcount == 0:
            code, response = 402, {"detail": "insufficient funds"}
        else:
            if crash_after_debit:
                raise RuntimeError("process died after the debit")
            payment_id = db.execute("INSERT INTO payments (user_id, amount_cents) VALUES (?, ?)", (user_id, amount)).lastrowid
            code, response = 201, {"payment_id": payment_id, "amount_cents": amount}
        db.execute("UPDATE idempotency SET status = 'completed', response_code = ?, response_body = ? "
                   "WHERE user_id = ? AND key = ?", (code, json.dumps(response), user_id, key))
        db.execute("COMMIT")
        return code, response, False
    except Exception:
        if db.in_transaction:
            db.execute("ROLLBACK")                       # the debit is undone...
        db.execute("DELETE FROM idempotency WHERE user_id = ? AND key = ? AND status = 'in_progress'", (user_id, key))
        raise                                            # ...and the key is free for a clean retry
```

Notes on decisions: a `402 insufficient funds` is stored as the key's result (a retry with the same key gets the same `402`; after the customer tops up, the client uses a **new** key). Unexpected errors (a crash, a `500`) are **not** stored: the key is released so the retry can run properly.

### 13.5 Proving it works

Every behaviour in the table gets a test. First the retry that broke the naive version, then the others:

```python run
import os
import tempfile

import payments as p
from payments_safe import create_payment

with tempfile.TemporaryDirectory() as tmp:
    path = os.path.join(tmp, "shop.db")
    p.init_db(path, {1: 10_000, 2: 10_000})
    body = {"amount_cents": 2_500}

    # 1. the lost-response scenario: the same key on both attempts
    first = create_payment(path, 1, "key-A", body)
    again = create_payment(path, 1, "key-A", body)             # the retry
    print("first  :", first)
    print("retry  :", again)
    print("payments:", p.payment_count(path, 1), "| balance:", p.balance(path, 1), "(charged once)")

    # 2. same key, different payload: a client bug, refused
    print("reuse  :", create_payment(path, 1, "key-A", {"amount_cents": 9_900})[:2])
    print("balance still", p.balance(path, 1))

    # 3. keys are per user: user 2 may use the same key text
    print("user 2 :", create_payment(path, 2, "key-A", body)[:2], "| user 2 balance:", p.balance(path, 2))

    # 4. a different key is a different payment
    print("new key:", create_payment(path, 1, "key-B", body)[:2], "| balance:", p.balance(path, 1))

    # 5. an error result is also replayed, not re-run
    print("too big:", create_payment(path, 1, "key-C", {"amount_cents": 99_999})[:2],
          "-> replay:", create_payment(path, 1, "key-C", {"amount_cents": 99_999})[2])
```
```text
first  : (201, {'payment_id': 1, 'amount_cents': 2500}, False)
retry  : (201, {'payment_id': 1, 'amount_cents': 2500}, True)
payments: 1 | balance: 7500 (charged once)
reuse  : (422, {'detail': 'this Idempotency-Key was already used with a different request'})
balance still 7500
user 2 : (201, {'payment_id': 2, 'amount_cents': 2500}) | user 2 balance: 7500
new key: (201, {'payment_id': 3, 'amount_cents': 2500}) | balance: 5000
too big: (402, {'detail': 'insufficient funds'}) -> replay: True
```

Now the two hard cases: a request that arrives while the first is still running, and a crash in the middle:

```python run
import os
import sqlite3
import tempfile

import payments as p
from payments_safe import LOCK_TIMEOUT, create_payment

with tempfile.TemporaryDirectory() as tmp:
    path = os.path.join(tmp, "shop.db")
    p.init_db(path, {1: 10_000})
    body = {"amount_cents": 4_000}

    # a crash after the debit: the transaction is rolled back, nothing is left behind
    try:
        create_payment(path, 1, "key-X", body, crash_after_debit=True)
    except RuntimeError as exc:
        print("crash      :", exc)
    print("after crash:", "balance", p.balance(path, 1), "| payments", p.payment_count(path, 1),
          "| key rows", p.connect(path).execute("SELECT COUNT(*) FROM idempotency").fetchone()[0])
    print("retry      :", create_payment(path, 1, "key-X", body)[:2], "| balance", p.balance(path, 1))

    # a request arrives while the first is "in progress" (simulate by inserting the claim row ourselves)
    fp = p.fingerprint_of(body)
    p.connect(path).execute("INSERT INTO idempotency (user_id, key, fingerprint, status, locked_at) VALUES (1,'key-Y',?,'in_progress',1000)", (fp,))
    print("in progress:", create_payment(path, 1, "key-Y", body, now=lambda: 1005.0)[:2])
    print("dead claim :", create_payment(path, 1, "key-Y", body, now=lambda: 1000.0 + LOCK_TIMEOUT + 1)[:2], "(taken over after the timeout)")
    print("balance    :", p.balance(path, 1))
```
```text
crash      : process died after the debit
after crash: balance 10000 | payments 0 | key rows 0
retry      : (201, {'payment_id': 1, 'amount_cents': 4000}) | balance 6000
in progress: (409, {'detail': 'a request with this key is still being processed'})
dead claim : (201, {'payment_id': 2, 'amount_cents': 4000}) (taken over after the timeout)
balance    : 2000
```

And the test that matters most, **real concurrency**: eight threads, each with its own database connection, send the same key at the same moment. Exactly one charge may happen:

```python run
import os
import tempfile
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import payments as p
from payments_safe import create_payment

with tempfile.TemporaryDirectory() as tmp:
    path = os.path.join(tmp, "shop.db")
    p.init_db(path, {1: 10_000})
    gate = Barrier(8)

    def attempt(_):
        gate.wait()                                              # release all threads at once
        return create_payment(path, 1, "same-key", {"amount_cents": 1_000})

    with ThreadPoolExecutor(8) as pool:
        results = list(pool.map(attempt, range(8)))

    outcomes = Counter((code, replayed) for code, _, replayed in results)
    print("status codes seen    :", sorted({code for code, _, _ in results}))
    print("executed (not replay):", sum(1 for code, _, replayed in results if code == 201 and not replayed))
    print("payment rows         :", p.payment_count(path, 1))
    print("balance              :", p.balance(path, 1), "(10000 - 1000)")
```
```text
status codes seen    : [201]
executed (not replay): 1
payment rows         : 1
balance              : 9000 (10000 - 1000)
```

Whatever order the threads run in, one 201 executes, the others are replays of it (`201`, replayed) or told to retry (`409`), and the balance drops once. The unique constraint, not luck, guarantees it.

### 13.6 The HTTP endpoint

The endpoint is thin: authenticate, require the header, call the function, translate the result. Everything that matters happens in one tested function:

```python run
import os
import tempfile

from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from pydantic import BaseModel, ConfigDict, Field

import payments as p
from payments_safe import create_payment

TOKENS = {"t-ada": 1}


class PaymentIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    amount_cents: int = Field(gt=0, le=1_000_000)


def build_app(path: str) -> FastAPI:
    app = FastAPI()

    @app.post("/payments")
    def post_payment(body: PaymentIn, authorization: str = Header(default=""),
                     idempotency_key: str | None = Header(default=None, min_length=8, max_length=64)):
        user_id = TOKENS.get(authorization.removeprefix("Bearer "))
        if user_id is None:
            raise HTTPException(401, "login required", headers={"WWW-Authenticate": "Bearer"})
        if idempotency_key is None:
            raise HTTPException(400, "the Idempotency-Key header is required for this endpoint")
        code, response, replayed = create_payment(path, user_id, idempotency_key, body.model_dump())
        headers = {"Idempotent-Replayed": "true"} if replayed else {}
        if code == 409:
            headers["Retry-After"] = "1"
        return JSONResponse(response, status_code=code, headers=headers)

    return app


with tempfile.TemporaryDirectory() as tmp:
    path = os.path.join(tmp, "shop.db")
    p.init_db(path, {1: 10_000})
    client = TestClient(build_app(path))
    auth = {"Authorization": "Bearer t-ada"}
    key = {"Idempotency-Key": "9f1c2d3e-0001"}

    r = client.post("/payments", json={"amount_cents": 2500}, headers=auth | key)
    print("first   :", r.status_code, r.json(), r.headers.get("idempotent-replayed"))
    r = client.post("/payments", json={"amount_cents": 2500}, headers=auth | key)
    print("retry   :", r.status_code, r.json(), r.headers.get("idempotent-replayed"))
    print("no key  :", client.post("/payments", json={"amount_cents": 2500}, headers=auth).status_code)
    print("bad body:", client.post("/payments", json={"amount_cents": -5}, headers=auth | key).status_code)
    print("anon    :", client.post("/payments", json={"amount_cents": 2500}, headers=key).status_code)
    print("balance :", p.balance(path, 1), "| payments:", p.payment_count(path, 1))
```
```text
first   : 201 {'payment_id': 1, 'amount_cents': 2500} None
retry   : 201 {'payment_id': 1, 'amount_cents': 2500} true
no key  : 400
bad body: 422
anon    : 401
balance : 7500 | payments: 1
```

### 13.7 The client's half of the contract

Idempotency keys only help if the client uses them correctly:

- Generate the key **once per logical operation** (when the user clicks "Pay"), **store it** (before sending), and reuse it for **every retry** of that operation. A fresh key per attempt defeats the whole mechanism.
- Retry only on **network errors, timeouts and `5xx`/`409`/`429`**; never retry a `4xx` that says the request is wrong.
- Use **exponential backoff with jitter** (wait 0.5 s, 1 s, 2 s... plus a random part), obey `Retry-After`, and set a maximum number of attempts. Many clients retrying in step make an outage worse ("thundering herd").
- A key that has been used for a result stays valid only for a while (24 hours is common); the server deletes old rows.

```python run
import random


def retry_delay(attempt: int, base: float = 0.5, cap: float = 8.0, rng=random.random) -> float:
    """Equal jitter: half fixed backoff, half random. attempt starts at 1."""
    backoff = min(cap, base * 2 ** (attempt - 1))
    return backoff / 2 + rng() * backoff / 2


print([round(retry_delay(n, rng=lambda: 0.0), 2) for n in range(1, 7)], "<- lower bound of each wait")
print([round(retry_delay(n, rng=lambda: 1.0), 2) for n in range(1, 7)], "<- upper bound")
```
```text
[0.25, 0.5, 1.0, 2.0, 4.0, 4.0] <- lower bound of each wait
[0.5, 1.0, 2.0, 4.0, 8.0, 8.0] <- upper bound
```

### 13.8 The same idea elsewhere

At-least-once delivery is the normal case in distributed systems: **webhooks** (dedupe on the event id, section 6.4), **message queues** (a consumer may get a message twice, swe.08), **scheduled jobs** that overlap, and **client retries** all need idempotent handlers. Whenever you hear "at least once", read "so it must be safe to do twice".

### Try it: what is wrong with this design?

A developer builds the idempotency check as "`if not exists(key): charge(); insert(key)`", with two separate statements and no transaction. Name two failures.

<details><summary>Answer</summary>

(1) **Race:** two requests with the same key both run `exists` before either runs `insert`, both see "not found", both charge. The claim must be a single atomic `INSERT` guarded by a unique constraint. (2) **Crash gap:** if the process dies between `charge()` and `insert(key)`, the money moved but the key is unknown, so the retry charges again. The work and the "completed" mark must share one transaction (or, for external systems, the key must be passed to them).

</details>

### Try it: key scope

If the idempotency table were keyed on `key` alone, what could a malicious customer do?

<details><summary>Answer</summary>

Send a request with a key they guessed or observed from another customer. Depending on the implementation they would receive that customer's stored response (a data leak: payment ids and amounts), or get a confusing `422`, or block the victim's operation. Scoping the key to the authenticated user (`PRIMARY KEY (user_id, key)`) removes the whole class of problems, and stored responses are never returned to anyone but their owner.

</details>

## 14. Input validation, injection and other unsafe operations

### 14.1 Principles

Almost every injection attack has the same shape: **untrusted data is interpreted as code or as a command** somewhere downstream: in SQL, a shell, a file path, HTML, a URL fetcher, a deserialiser, a template. Defending is a habit, not a library:

1. **Validate at the boundary, by allow-list.** Say what is valid (type, range, length, format, set of values) and reject everything else. Block-lists ("no `<script>`") always miss a case.
2. **Canonicalise before you validate.** Normalise Unicode, decode URL escapes once, lower-case, strip: the check and the use must see the same value.
3. **Separate code from data.** Parameterised queries, argument lists instead of command strings, template engines with autoescape: the interpreter must never be able to mistake data for instructions.
4. **Encode on output** for the place the data is going (HTML, URL, SQL, shell).
5. **Limit size and count**: a field with no maximum length, or a list with no maximum item count, is a denial-of-service lever.

Validation is not sanitisation is not encoding: *validation* rejects bad input, *sanitisation* tries to clean it (fragile; prefer rejecting), *encoding* makes data safe for a specific output. You need the first and last far more often than the middle one.

### 14.2 Validation with Pydantic

You learned this machinery in swe.05 section 5. The security habits:

```python run
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, ValidationError

Sku = Annotated[str, StringConstraints(pattern=r"^[A-Z0-9-]{3,20}$", strip_whitespace=True)]


class OrderLine(BaseModel):
    model_config = ConfigDict(extra="forbid")                   # unknown fields are errors, not silently dropped
    sku: Sku
    quantity: int = Field(ge=1, le=99)


class OrderIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    lines: list[OrderLine] = Field(min_length=1, max_length=50)       # a bound on list size
    shipping: Literal["standard", "express"]                           # an allow-list of values
    note: str = Field(default="", max_length=500)                      # a bound on text size


good = {"lines": [{"sku": " ab-12 ".upper(), "quantity": 2}], "shipping": "express"}
print("valid     :", OrderIn(**good).lines[0].sku)

attacks = {
    "is_admin field": {**good, "is_admin": True},
    "huge list": {**good, "lines": [{"sku": "AB-12", "quantity": 1}] * 10_000},
    "quantity -5": {**good, "lines": [{"sku": "AB-12", "quantity": -5}]},
    "sql in sku": {**good, "lines": [{"sku": "x'; DROP TABLE orders;--", "quantity": 1}]},
    "unknown shipping": {**good, "shipping": "teleport"},
    "5 MB note": {**good, "note": "A" * 5_000_000},
}
for label, payload in attacks.items():
    try:
        OrderIn(**payload)
        print(f"{label:17} ACCEPTED (bug!)")
    except ValidationError as exc:
        print(f"{label:17} rejected:", exc.errors()[0]["type"])
```
```text
valid     : AB-12
is_admin field    rejected: extra_forbidden
huge list         rejected: too_long
quantity -5       rejected: greater_than_equal
sql in sku        rejected: string_pattern_mismatch
unknown shipping  rejected: literal_error
5 MB note         rejected: string_too_long
```

Validation by pattern does not make SQL safe (the next sections do that), but it removes huge classes of unexpected values early and makes later code easier to reason about.

### 14.3 SQL injection

SQL injection happens when user text becomes part of the SQL *statement*. The classic login bypass:

```python run
import sqlite3

db = sqlite3.connect(":memory:")
db.executescript("""
    CREATE TABLE users (name TEXT, password TEXT);
    INSERT INTO users VALUES ('ada', 'secret-ada'), ('admin', 'secret-admin');
""")


def login_vulnerable(name, password):
    sql = f"SELECT name FROM users WHERE name = '{name}' AND password = '{password}'"      # BUG: string building
    return db.execute(sql).fetchall()


def login_safe(name, password):
    return db.execute("SELECT name FROM users WHERE name = ? AND password = ?", (name, password)).fetchall()


attack = "' OR '1'='1"
print("vulnerable, wrong password :", login_vulnerable("ada", "nope"))
print("vulnerable, attacker       :", login_vulnerable("ada", attack))
print("safe, attacker             :", login_safe("ada", attack))
print("safe, the attacker as name :", login_safe("admin' --", "x"))
```
```text
vulnerable, wrong password : []
vulnerable, attacker       : [('ada',), ('admin',)]
safe, attacker             : []
safe, the attacker as name : []
```

The attacker's text closed the quote and added `OR '1'='1'`, making the `WHERE` always true. With the **placeholder** (`?`, or `%s` in other drivers) the database receives the SQL and the values separately, so the value can never become SQL. Rules:

- **Always use placeholders for values**, even for integers and "trusted" data. It is also faster, since the database can reuse the plan.
- Placeholders cannot be used for **identifiers** (table or column names, `ASC`/`DESC`). Map user choices through an allow-list (section 10.4).
- **ORMs are not magic.** `Model.objects.raw(f"...")`, `text(f"...")` in SQLAlchemy, and `cursor.execute(f"...")` are as injectable as the example. Use the bound-parameter forms.
- **Second-order injection:** a value stored safely today (a username like `x'; DROP...`) is later pasted into a query by another piece of code. Treat data from the database as untrusted too.
- `LIKE` wildcards (`%`, `_`) in user input change the meaning of a search; escape them (`ESCAPE '\\'`) if literal matching is intended.
- Give the application's database user **only the permissions it needs** (no `DROP`, no access to other schemas). A successful injection then does less damage.

### 14.4 Command injection

Passing user text to a shell lets the shell interpret `;`, `&&`, `$()` and backticks:

```python run
import subprocess
import sys

filename = "photo.jpg; echo INJECTED-COMMAND-RAN"


def run(*args, **kw):
    return subprocess.run(*args, capture_output=True, text=True, **kw).stdout.strip().splitlines()


print("shell=True with a formatted string (vulnerable):", run(f"echo converting {filename}", shell=True))
print("argument list, no shell (safe)                 :", run(["echo", "converting", filename]))
print("the program receives one harmless argument     :", run([sys.executable, "-c", "import sys; print(sys.argv[1:])", filename]))
```
```text
shell=True with a formatted string (vulnerable): ['converting photo.jpg', 'INJECTED-COMMAND-RAN']
argument list, no shell (safe)                 : ['converting photo.jpg; echo INJECTED-COMMAND-RAN']
the program receives one harmless argument     : ["['photo.jpg; echo INJECTED-COMMAND-RAN']"]
```

The first list has a second line: the attacker's `echo` command ran. The rule: **never `shell=True` with anything user-controlled**; pass a list of arguments, so no shell parses them. Also avoid `os.system`, `eval` and `exec` on user data. If you must build a shell string, `shlex.quote()` each piece, as a last resort.

### 14.5 Path traversal and file uploads

A file name from the client is untrusted text. `../../etc/passwd` walks out of your upload folder:

```python run
import tempfile
from pathlib import Path

with tempfile.TemporaryDirectory() as tmp:
    UPLOADS = (Path(tmp) / "uploads").resolve()
    UPLOADS.mkdir()
    (Path(tmp) / "secrets.txt").write_text("top secret")

    def open_vulnerable(name: str) -> str:
        return (UPLOADS / name).read_text()                       # BUG: trusts the name

    def open_safe(name: str) -> str:
        target = (UPLOADS / name).resolve()                       # resolve ".." and symlinks first
        if not target.is_relative_to(UPLOADS):                    # then check where we ended up
            raise PermissionError("path escapes the upload folder")
        return target.read_text()

    print("vulnerable:", open_vulnerable("../secrets.txt"))
    try:
        open_safe("../secrets.txt")
    except PermissionError as exc:
        print("safe      :", exc)
    for sneaky in ("/etc/hostname", "ok/../../secrets.txt"):
        try:
            open_safe(sneaky)
        except (PermissionError, FileNotFoundError) as exc:
            print(f"{sneaky:22}", type(exc).__name__)
```
```text
vulnerable: top secret
safe      : path escapes the upload folder
/etc/hostname          PermissionError
ok/../../secrets.txt   PermissionError
```

For **file uploads** the list is longer:

- Never use the client's file name for storage. Generate your own (`uuid4().hex`) and keep the original only as display text (`Path(name).name` strips directories).
- Limit **size** (section 11.7) and **count**; check the **extension against an allow-list** *and* the actual content (the first bytes "magic numbers": PNG starts with `\x89PNG`), because the `Content-Type` header is chosen by the client.
- Store files **outside the web root**, or in object storage, and serve them with a fixed `Content-Type` and `Content-Disposition: attachment`, so an uploaded `.html` file can never run as a page on your domain.
- Never execute or `import` an upload. Scan for malware if the files are shared with others.
- Archives (`zip`, `tar`) can contain `../` entries ("zip slip") and enormous expansions ("zip bomb"); check member paths and total size before extracting.

### 14.6 SSRF: making your server fetch something dangerous

**Server-side request forgery**: the feature "give us a URL and we fetch it" (webhook URL, avatar import, link preview) turns your server into the attacker's proxy. They give `http://169.254.169.254/latest/meta-data/` (the cloud metadata service, which hands out credentials) or `http://localhost:6379/` (your internal Redis). The request comes from *inside* your network, which firewalls trust.

Defences, combined:

1. **Allow-list** schemes (`https` only) and, if you can, destination hosts.
2. **Resolve the host name to IP addresses yourself and reject non-public ones** (loopback, private ranges, link-local, reserved).
3. **Connect to the IP you validated**, because DNS can answer differently the second time ("DNS rebinding").
4. **Do not follow redirects blindly** (a public URL can redirect to `http://169.254...`); re-validate every hop.
5. Put the fetcher in a network segment with no access to internal services, and apply timeouts and size limits.

The IP check is a good use of the standard library:

```python run
import ipaddress
from urllib.parse import urlparse


def check_url(url: str) -> str:
    parts = urlparse(url)
    if parts.scheme != "https":
        return "refused: only https"
    host = parts.hostname or ""
    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        return "needs DNS: resolve it, then run the same check on every address returned"
    if ip.version == 6 and ip.ipv4_mapped:                         # ::ffff:127.0.0.1 hides an IPv4 address
        ip = ip.ipv4_mapped
    return "allowed" if ip.is_global else f"refused: {ip} is not a public address"


for url in ["https://93.184.216.34/hook", "https://127.0.0.1/admin", "https://169.254.169.254/latest/meta-data/",
            "https://10.0.0.5:6379/", "https://[::1]/", "https://[::ffff:127.0.0.1]/", "http://93.184.216.34/",
            "https://hooks.example.com/pay"]:
    print(f"{url:45} {check_url(url)}")
```
```text
https://93.184.216.34/hook                    allowed
https://127.0.0.1/admin                       refused: 127.0.0.1 is not a public address
https://169.254.169.254/latest/meta-data/     refused: 169.254.169.254 is not a public address
https://10.0.0.5:6379/                        refused: 10.0.0.5 is not a public address
https://[::1]/                                refused: ::1 is not a public address
https://[::ffff:127.0.0.1]/                   refused: 127.0.0.1 is not a public address
http://93.184.216.34/                         refused: only https
https://hooks.example.com/pay                 needs DNS: resolve it, then run the same check on every address returned
```

`ip.is_global` is the key property: it is `False` for loopback, private, link-local and other reserved ranges. (Some exotic forms such as the integer `2130706433` or hex `0x7f000001` are normalised by the operating system's resolver but not by `ipaddress`; that is why you must validate the **resolved** addresses, not the text of the URL.)

### 14.7 Unsafe deserialisation

Some formats can run code while loading. **`pickle`** is the best-known: loading a pickle from an untrusted source is remote code execution by design.

```python run
import json
import pickle


class Evil:
    def __reduce__(self):                                         # tells pickle how to rebuild the object...
        return (print, ("code ran just from loading this pickle!",))      # ...by calling any function the attacker likes


payload = pickle.dumps(Evil())
print("loading the untrusted bytes:")
pickle.loads(payload)                                             # the print runs; it could have been os.system(...)

print("loading JSON instead      :", json.loads('{"a": 1}'))
```
```text
loading the untrusted bytes:
code ran just from loading this pickle!
loading JSON instead      : {'a': 1}
```

Rules: never `pickle.loads`, `marshal.loads` or `yaml.load` (without a safe loader) on data from outside your trust boundary. Use **JSON** (or Pydantic models) for data that crosses a boundary; `yaml.safe_load` for YAML; for XML use `defusedxml` (XML parsers can fetch files or URLs and expand "billion laughs" entities; `defusedxml` is not installed here, so this is described rather than run). Be wary of any "load a model/object from a file the user supplied" feature, including machine-learning model files, which are often pickles.

### 14.8 Open redirects

A login page that obeys `?next=https://evil.example` sends users to a look-alike site right after they type their password. Allow only **local paths**. The details matter, because browsers are forgiving:

```python run
from urllib.parse import urlparse


def safe_next(target: str, default: str = "/") -> str:
    if not target or "\\" in target:                               # browsers treat \ like /
        return default
    parts = urlparse(target)
    if parts.scheme or parts.netloc:                               # "https://evil", "//evil", "javascript:..."
        return default
    if not target.startswith("/") or target.startswith("//"):
        return default
    return target


for target in ["/orders", "/orders?page=2", "https://evil.example", "//evil.example", "/\\evil.example",
               "https:evil.example", "javascript:alert(1)", "orders", ""]:
    print(f"{target!r:26} -> {safe_next(target)!r}")
```
```text
'/orders'                  -> '/orders'
'/orders?page=2'           -> '/orders?page=2'
'https://evil.example'     -> '/'
'//evil.example'           -> '/'
'/\\evil.example'          -> '/'
'https:evil.example'       -> '/'
'javascript:alert(1)'      -> '/'
'orders'                   -> '/'
''                         -> '/'
```

`/\evil.example` is the trap: Python's `urlparse` sees no host, but a browser turns the backslash into a slash and goes to `//evil.example`. Reject backslashes, and require "starts with `/` and not with `//`". Or avoid user-controlled redirects: store the destination server-side and send only an opaque id.

### 14.9 Output: headers and encoding

Escape for the place data goes to. For HTML, use a template engine with autoescape (Jinja2, Django: swe.04, swe.06). A JSON API should set the right `Content-Type`, so browsers do not guess. A few **security headers** add cheap defence in depth:

| Header | Effect |
|---|---|
| `Strict-Transport-Security` | browsers use HTTPS only for your site (after the first visit) |
| `X-Content-Type-Options: nosniff` | the browser trusts the declared type; no guessing "this JSON looks like HTML" |
| `Content-Security-Policy` | restricts where scripts, styles and frames may come from; the strongest XSS mitigation |
| `X-Frame-Options: DENY` or CSP `frame-ancestors 'none'` | blocks clickjacking by forbidding framing |
| `Referrer-Policy: no-referrer` (or `strict-origin-when-cross-origin`) | do not leak URLs to other sites |
| `Cache-Control: no-store` on sensitive responses | no personal data left in shared caches |

```python run
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

app = FastAPI()
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Content-Security-Policy": "default-src 'none'; frame-ancestors 'none'",       # an API returns data, not pages
}


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    for name, value in SECURITY_HEADERS.items():
        response.headers.setdefault(name, value)
    if request.url.path.startswith("/me"):
        response.headers["Cache-Control"] = "no-store"
    return response


@app.get("/me")
def me():
    return {"name": "ada"}


r = TestClient(app).get("/me")
for name in [*SECURITY_HEADERS, "Cache-Control"]:
    print(f"{name:27}", r.headers.get(name))
```
```text
X-Content-Type-Options      nosniff
X-Frame-Options             DENY
Referrer-Policy             no-referrer
Strict-Transport-Security   max-age=31536000; includeSubDomains
Content-Security-Policy     default-src 'none'; frame-ancestors 'none'
Cache-Control               no-store
```

### 14.10 One more: regular-expression denial of service

A badly written pattern such as `^(a+)+$` takes exponential time on input like `aaaa...!`, so a single request can occupy a CPU for minutes (core.18 explains why). Avoid nested quantifiers, bound the input length **before** matching, and prefer simple parsers to clever patterns when the input is untrusted.

### Try it: spot every flaw

```python
@app.get("/download")
def download(name: str, next: str):
    data = open(f"/srv/files/{name}", "rb").read()
    os.system(f"clamscan /srv/files/{name}")
    return RedirectResponse(next)
```

List the vulnerabilities.

<details><summary>Answer</summary>

(1) **Path traversal**: `name=../../etc/passwd` reads any file; resolve and check `is_relative_to`, or look the file up by an id. (2) **Command injection**: `name` is placed in a shell command (`name=x; rm -rf ~`); use `subprocess.run(["clamscan", path])` without a shell. (3) **Open redirect**: `next` is used unchecked. (4) **No authorisation**: any caller downloads any file (IDOR, section 8). (5) The file is read fully into memory with no size limit. (6) It returns a redirect from a `download` endpoint, which is confusing design; and nothing is logged. One snippet, six problems: this is how real code looks.

</details>

### Try it: why resolve before checking?

Why does `open_safe` call `.resolve()` before `is_relative_to`, rather than checking whether the name contains `".."`?

<details><summary>Answer</summary>

Checking for the text `".."` is a block-list: it misses encoded forms, absolute paths (`/etc/passwd`), and **symlinks** inside the upload folder that point outside. `.resolve()` produces the real, final path, and the check then compares that to the folder. Check the thing you will actually use, not a description of it.

</details>


## 15. Secrets, logging, errors and dependencies

### 15.1 What counts as a secret

Anything that grants access if someone else holds it: database passwords, API keys, JWT signing keys and peppers, OAuth client secrets, session-signing keys, cloud credentials, TLS private keys, webhook secrets, and user tokens. The rules are short and are broken constantly:

- **Never in source code or in git.** Git remembers forever; a secret removed in a later commit is still in the history, and public repositories are scanned by bots within minutes.
- **Never in logs, error messages, URLs, screenshots or support tickets.**
- **One secret per purpose and per environment.** The test key must not open production.
- **Least privilege.** The app's database user needs `SELECT/INSERT/UPDATE` on its tables, not superuser rights.
- **Rotate** on a schedule, and immediately after anyone who knew it leaves or a leak is possible.

### 15.2 Where secrets live

| Place | Fine for | Notes |
|---|---|---|
| **Environment variables** | the usual way to pass secrets into a process ("twelve-factor") | visible to child processes and to anyone who can read `/proc/<pid>/environ`; never print `os.environ` in a debug page or log |
| **`.env` file** | local development | listed in `.gitignore`; commit a `.env.example` with fake values |
| **Secret manager** (AWS Secrets Manager, Google Secret Manager, HashiCorp Vault, Azure Key Vault) | production | access control, audit trail, rotation, injected at start-up |
| **CI/CD secret store** | pipelines | masked in logs; scope per environment |
| **Kubernetes `Secret`** | clusters | only base64-**encoded**, not encrypted, unless you enable encryption at rest; restrict who can read them |
| **Source code, config committed to git, Docker image layers** | **never** | an image is a file you ship to a registry |

### 15.3 Configuration that fails fast and stays quiet

Read secrets once at start-up, **refuse to start** if one is missing or too weak (a service that boots with a default key is worse than one that does not boot), and keep them in a type that does not print itself:

```python run
import os
from pydantic import BaseModel, SecretStr, ValidationError, field_validator


class Settings(BaseModel):
    database_url: SecretStr
    jwt_secret: SecretStr
    debug: bool = False

    @field_validator("jwt_secret")
    @classmethod
    def long_enough(cls, value: SecretStr) -> SecretStr:
        if len(value.get_secret_value()) < 32:
            raise ValueError("JWT secret must be at least 32 characters")
        return value

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(database_url=os.environ.get("APP_DATABASE_URL", ""), jwt_secret=os.environ.get("APP_JWT_SECRET", ""),
                   debug=os.environ.get("APP_DEBUG") == "1")


os.environ["APP_DATABASE_URL"] = "postgresql://shop:hunter2@db/prod"
os.environ["APP_JWT_SECRET"] = "short"
try:
    Settings.from_env()
except ValidationError as exc:
    print("refused to start:", exc.errors()[0]["msg"])

os.environ["APP_JWT_SECRET"] = "x" * 40
settings = Settings.from_env()
print("repr hides it :", settings)
print("log line      :", f"starting with {settings.database_url}")
print("use it on purpose:", settings.database_url.get_secret_value().split("@")[1])
```
```text
refused to start: Value error, JWT secret must be at least 32 characters
repr hides it : database_url=SecretStr('**********') jwt_secret=SecretStr('**********') debug=False
log line      : starting with **********
use it on purpose: db/prod
```

`SecretStr` prints as `**********`, so an accidental `print(settings)` or log line does not leak. Reading the real value needs the explicit `get_secret_value()`, which is easy to search for in code review. Note also that the missing secrets case produced an *error at start-up*, not a runtime surprise at 3 a.m.

### 15.4 Random numbers: `secrets`, not `random`

`random` is a fast, **predictable** generator (Mersenne Twister). If an attacker sees enough outputs, they can compute the next ones. Anything that must be unguessable (session ids, reset tokens, API keys, CSRF tokens, passwords) comes from `secrets` (the operating system's secure source):

```python run
import random
import secrets

random.seed(1234)
first = [random.randrange(10**6) for _ in range(3)]
random.seed(1234)
second = [random.randrange(10**6) for _ in range(3)]
print("random, same seed       :", first == second, "<- fully predictable")
print("secrets.token_urlsafe(32):", len(secrets.token_urlsafe(32)), "chars, never repeats")
print("secrets.token_hex(16)    :", len(secrets.token_hex(16)), "hex chars =", 16 * 8, "bits")
print("secrets.choice picks      :", secrets.choice("abcdef") in "abcdef")
print("compare_digest           :", secrets.compare_digest("abc", "abc"), secrets.compare_digest("abc", "abd"))
```
```text
random, same seed       : True <- fully predictable
secrets.token_urlsafe(32): 43 chars, never repeats
secrets.token_hex(16)    : 32 hex chars = 128 bits
secrets.choice picks      : True
compare_digest           : True False
```

Rule of thumb: at least **128 random bits** for identifiers (16 bytes), **256 bits** for keys (32 bytes). Compare secrets with `secrets.compare_digest`, never `==`.

### 15.5 Finding secrets before an attacker does

Scan your repository for secrets as part of every commit and CI run: tools such as **gitleaks**, **trufflehog**, `detect-secrets`, and the secret scanning built into GitHub and GitLab. They look for known key shapes (a cloud access key starts with `AKIA...`; private keys begin with `-----BEGIN ... PRIVATE KEY-----`), for assignments like `password = "..."`, and for random-looking strings (**high entropy**). The core idea fits in a few lines:

```python run
import math
import re
from collections import Counter

PATTERNS = {
    "cloud access key id": re.compile(r"AKIA[0-9A-Z]{16}"),
    "private key": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "hard-coded password": re.compile(r"""(?i)(password|passwd|secret|api[_-]?key)\s*[=:]\s*['"][^'"]{6,}['"]"""),
}


def entropy(text: str) -> float:
    counts = Counter(text)
    return -sum(n / len(text) * math.log2(n / len(text)) for n in counts.values())


def scan(text: str):
    findings = []
    for lineno, line in enumerate(text.splitlines(), 1):
        for name, pattern in PATTERNS.items():
            if pattern.search(line):
                findings.append((lineno, name))
        for word in re.findall(r"[A-Za-z0-9+/=_-]{24,}", line):
            if entropy(word) > 4.0:
                findings.append((lineno, f"high-entropy string ({entropy(word):.1f} bits/char)"))
    return findings


sample = '''import boto3
AWS_KEY = "AKIAIOSFODNN7EXAMPLE"
DB_PASSWORD = "correct-horse-battery"
session = boto3.client("s3")
TOKEN = "q8Zr3KJd0aXw2nPvLm7YtB5sHcUe9GfA"
url = "https://example.com/some/very/long/readable/path"
'''
for lineno, what in scan(sample):
    print(f"line {lineno}: {what}")
```
```text
line 2: cloud access key id
line 3: hard-coded password
line 5: high-entropy string (5.0 bits/char)
```

(The example key `AKIAIOSFODNN7EXAMPLE` is the documented dummy value from cloud provider docs.) Real scanners have many more rules and fewer false positives, but this is the mechanism. Two practices matter more than the tool:

1. **Run it before the commit** (a `pre-commit` hook) *and* in CI, because developers skip local hooks.
2. **If a secret leaks, rotate it first.** Removing it from git history (`git filter-repo`) is secondary: assume it was copied. Then find out what it could access, and check the logs for use.

### 15.6 Logging for security

Logs are how you find out what happened. They are also a common source of leaks.

**What to log (events with security meaning):** successful and failed logins, password and e-mail changes, MFA events, token refresh and reuse, permission denials (`403`/`404` on someone else's object), admin actions, payments and refunds, rate-limit hits, validation failures that look like probing, and changes to roles. Each entry needs **who** (user id, never the password), **what**, **which object**, **when** (UTC), **where from** (IP, client), and a **correlation/request id** so one request can be followed across services.

**What never to log:** passwords (even wrong ones: a mistyped password is often one letter away from the real one), tokens, API keys, session ids, full card numbers, private keys, and personal data you do not need. Authorisation headers and request bodies need **redaction**:

```python run
import logging
import re


class Redact(logging.Filter):
    """Mask secrets in every log message before it is written."""
    PATTERNS = [
        (re.compile(r"(?i)(authorization['\"]?\s*[:=]\s*['\"]?)(bearer\s+)?[\w.~+/-]+"), r"\1[REDACTED]"),
        (re.compile(r"(?i)(password['\"]?\s*[:=]\s*['\"]?)[^\s'\",&]+"), r"\1[REDACTED]"),
        (re.compile(r"\b\d{13,16}\b"), "[CARD]"),
    ]

    def filter(self, record: logging.LogRecord) -> bool:
        message = record.getMessage()
        for pattern, replacement in self.PATTERNS:
            message = pattern.sub(replacement, message)
        record.msg, record.args = message, None
        return True


handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(levelname)s %(message)s"))
handler.addFilter(Redact())
log = logging.getLogger("audit")
log.addHandler(handler)
log.setLevel(logging.INFO)
log.propagate = False

log.warning("login failed for ada, password=hunter2 from 10.0.0.9")
log.info("request headers: {'Authorization': 'Bearer eyJhbGciOi.payload.sig', 'Accept': 'json'}")
log.info("charging card 4111111111111111 for order 17")
log.info("order 17 cancelled by user 1")                   # unchanged: nothing sensitive
```
```text
WARNING login failed for ada, password=[REDACTED] from 10.0.0.9
INFO request headers: {'Authorization': '[REDACTED]', 'Accept': 'json'}
INFO charging card [CARD] for order 17
INFO order 17 cancelled by user 1
```

A redaction filter is a **safety net**, not a licence to log secrets: the best protection is never putting them in the message.

**Log injection:** if you write user text straight into a log line, a user can add a newline and forge entries:

```python run
import json
import logging
import sys

logging.basicConfig(format="%(message)s", level=logging.INFO, stream=sys.stdout)
username = "ada\nINFO admin logged in from 10.0.0.1 successfully"        # attacker-controlled
logging.info("login failed for %s", username)                              # plain text log: forged second line!
print("--- same event as one JSON line per record ---")
print(json.dumps({"event": "login_failed", "username": username}))
```
```text
login failed for ada
INFO admin logged in from 10.0.0.1 successfully
--- same event as one JSON line per record ---
{"event": "login_failed", "username": "ada\nINFO admin logged in from 10.0.0.1 successfully"}
```

The plain-text log now contains a line that looks like a different event. **Structured (JSON) logging** escapes newlines inside values, so one record is always one line, and makes the logs searchable. Keep audit logs **append-only** and shipped to a separate system (the person who breaks in should not be able to erase their tracks), with retention and time synchronisation. A log nobody reads is useless: alert on bursts of `401`s, `403`s and `429`s.

### 15.7 Errors and defaults

- Return **generic errors** to clients with an incident id (section 9.4); keep detail in logs.
- **Debug mode off** in production. Flask's `debug=True` exposes the Werkzeug debugger, an interactive console that runs code; Django's `DEBUG = True` shows settings and SQL (swe.06 section 17).
- **Interactive docs and schema:** `/docs`, `/redoc` and `/openapi.json` list every route and field. Fine for public APIs; turn them off or protect them for internal ones (`FastAPI(docs_url=None, redoc_url=None, openapi_url=None)`).
- **Change default credentials**, remove sample accounts, disable directory listing and unused HTTP methods and endpoints (`/debug`, `/metrics` should not be public).
- **CORS** (swe.05 section 13) is a browser rule, not authentication: `allow_origins=["*"]` is fine for a public read-only API and dangerous together with credentials.
- Hide server banners and framework versions where you can; they save attackers a step.

### 15.8 Dependencies and the supply chain

Your code is a small part of what runs. Every installed package is code you trust.

- **Pin versions** (a lock file: `pip-tools`, `uv.lock`, Poetry) so builds are repeatable and nothing changes silently; update deliberately.
- **Scan for known vulnerabilities**: `pip-audit`, GitHub Dependabot, `safety`. Subscribe to advisories for your main frameworks and **patch quickly**: attackers read the same advisories.
- **Verify what you install**: `pip install --require-hashes -r requirements.txt` checks each file's hash. Beware **typosquatting** (`reqeusts`, `python-dateutils`) and packages that were taken over.
- **Keep the set small.** Each extra package is an extra risk and an upgrade chore. Remove what you no longer use.
- **Build in CI from a clean environment** and keep build credentials separate. Use minimal base images for containers, run as a non-root user, and do not copy `.env` or `.git` into images.

> **Try it on your machine** (needs network and a package index, so it is not run here):
>
> ```bash
> pip install pip-audit
> pip-audit
> ```
>
> Expected: either `No known vulnerabilities found`, or a table listing each vulnerable package, the installed version, the advisory id and the version that fixes it. The result depends on today's advisory database and your installed packages, so no output is shown.

### 15.9 Cryptography: choose the right tool, never invent one

| Need | Tool | Example |
|---|---|---|
| store a password | slow salted hash | scrypt, Argon2id, bcrypt (section 2) |
| check a file or message was not changed (no secret) | hash | SHA-256 (`hashlib`) |
| prove a message came from a holder of a shared secret | **MAC** | HMAC-SHA256 (`hmac`): webhooks, signed cookies |
| prove a message came from the holder of a private key | **digital signature** | RS256/ES256/EdDSA JWTs |
| keep data secret | **authenticated encryption** | AES-GCM, ChaCha20-Poly1305, `Fernet` from the `cryptography` package |
| generate unguessable values | CSPRNG | `secrets` |

Rules: do not design your own algorithm or protocol; use **authenticated** encryption (it detects tampering, plain AES-CBC/ECB do not); never reuse a nonce with the same key; derive keys from passwords only with a KDF (scrypt, PBKDF2); use TLS for data in transit. The `cryptography` package is not installed in this environment, so encryption is described here rather than run. What *is* available is `itsdangerous`, which Flask uses for signed values, perfect for **e-mail confirmation and invitation links**: the token carries data, is signed, and expires, and a different `salt` per purpose stops a token for one use being accepted for another:

```python run
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

KEY = "k" * 40                                                       # in real life: from the environment
confirm = URLSafeTimedSerializer(KEY, salt="email-confirm")
reset = URLSafeTimedSerializer(KEY, salt="password-reset")

token = confirm.dumps({"user_id": 7})
print("payload is readable but signed:", confirm.loads(token, max_age=3600))
try:
    confirm.loads(token, max_age=-1)                                 # pretend it is already too old
except SignatureExpired:
    print("expired token  : SignatureExpired")
try:
    reset.loads(token)                                               # same key, different purpose
except BadSignature:
    print("wrong purpose  : BadSignature")
try:
    confirm.loads(token[:-2] + "xx")
except BadSignature:
    print("tampered token : BadSignature")
```
```text
payload is readable but signed: {'user_id': 7}
expired token  : SignatureExpired
wrong purpose  : BadSignature
tampered token : BadSignature
```

### Try it: where should the secret live?

For each, choose where it belongs: (a) the JWT signing key in production; (b) the same key on your laptop; (c) the public client id of an OAuth app; (d) a webhook secret for a partner integration.

<details><summary>Answer</summary>

(a) A secret manager (or an environment variable injected at deploy time from the platform's secret store), different from every other environment. (b) A local `.env` file ignored by git, with a *different* value. (c) The client id is not secret; it can be in code or configuration (the client *secret* is). (d) A secret manager or environment variable; also stored per partner so that you can rotate one without affecting others, and shown to the partner once.

</details>

### Try it: the logged password

A teammate logs `logger.warning("login failed: %s / %s", username, password)` "to help debugging". Give two reasons that this is dangerous.

<details><summary>Answer</summary>

(1) Anyone with log access (developers, support, a log vendor, an attacker who reads the files) can read the passwords, and logs are copied around and kept for months. (2) Failed passwords are often typos of the correct one, or the user's password for another site that they typed into the wrong place, so they are as sensitive as real passwords. Log the username, the reason and the source address only.

</details>

## 16. The OWASP Top 10, read as a Python developer

**OWASP** (the Open Worldwide Application Security Project) publishes the best-known list of web application risks, the **Top 10**, and a separate **API Security Top 10**. The lists are updated every few years, so check owasp.org for the current edition; the version below is the 2021 web list, which many courses and audits still use. The names are written from memory and the categories are stable. The goal here is not memorising the list but knowing where each one lives in Python code.

| # | Category | Typical Python form | This chapter |
|---|---|---|---|
| A01 | **Broken access control** | missing ownership or role check, IDOR, mass assignment | 7, 8 |
| A02 | **Cryptographic failures** | plain-text or fast-hashed passwords, `random` for tokens, no TLS, secrets in git | 2, 4, 15 |
| A03 | **Injection** | f-string SQL, `shell=True`, `eval`, template injection | 14 |
| A04 | **Insecure design** | no rate limit, no idempotency, no threat model, business-logic flaws | 1, 11, 13 |
| A05 | **Security misconfiguration** | `DEBUG=True`, default passwords, open docs, permissive CORS, verbose errors | 9.4, 15.7 |
| A06 | **Vulnerable and outdated components** | unpinned, unpatched packages | 15.8 |
| A07 | **Identification and authentication failures** | weak passwords, enumeration, no MFA, session fixation, bad JWT checks | 2, 3, 4, 5, 6 |
| A08 | **Software and data integrity failures** | `pickle.loads` of untrusted data, unsigned updates, trusting CI plugins, unsigned webhooks | 6.4, 14.7, 15.8 |
| A09 | **Security logging and monitoring failures** | no audit trail, secrets in logs, no alerts | 15.6 |
| A10 | **Server-side request forgery** | fetching user-supplied URLs | 14.6 |

The companion **API Security Top 10 (2023)** uses API wording for the same ideas: BOLA (object-level authorisation, section 8), broken authentication, broken object *property* level authorisation (mass assignment and data exposure), unrestricted resource consumption (section 11), BFLA (function-level authorisation), unrestricted access to sensitive business flows (abuse of valid features, such as ticket scalping or coupon farming: rate limits and idempotency), SSRF, security misconfiguration, improper inventory management (forgotten old versions and hosts, section 12.5), and unsafe consumption of APIs (trusting third-party responses without validating them).

### 16.1 Python-specific footguns

A few traps are specific to the language and its standard library:

**`assert` is not a security check.** Python removes `assert` statements when run with `-O` (optimised mode), and some deployments use it. A permission check written as `assert user.is_admin` disappears:

```python run
import subprocess
import sys

program = "def delete_everything(is_admin):\n    assert is_admin, 'admins only'\n    return 'deleted'\nprint(delete_everything(False))"
normal = subprocess.run([sys.executable, "-c", program], capture_output=True, text=True)
optimised = subprocess.run([sys.executable, "-O", "-c", program], capture_output=True, text=True)
print("normal run   :", normal.stderr.strip().splitlines()[-1])
print("python -O run:", optimised.stdout.strip(), "<- the check vanished")
```
```text
normal run   : AssertionError: admins only
python -O run: deleted <- the check vanished
```

Use `if not is_admin: raise PermissionError`, and keep `assert` for tests and internal consistency checks.

**User-controlled format strings leak attributes.** `str.format` can read attributes of the objects you pass in. If a *user* supplies the template (a "customise your e-mail" feature), they can read fields you never meant to show:

```python run
from string import Template


class User:
    def __init__(self):
        self.name = "ada"
        self.password_hash = "scrypt$16384$8$1$salt$hash"


user_template = "Hello {user.name}, your hash is {user.password_hash}"        # written by the attacker
print("str.format :", user_template.format(user=User()))
print("Template   :", Template("Hello $name").safe_substitute(name="ada"), "<- no attribute access possible")
```
```text
str.format : Hello ada, your hash is scrypt$16384$8$1$salt$hash
Template   : Hello ada <- no attribute access possible
```

Use `string.Template` (or a sandboxed template engine) for user-supplied templates. A related bug in web frameworks is **server-side template injection**: passing user text to `render_template_string()` (Flask) or `Template(user_text)` (Jinja2) lets the attacker run template expressions, and on an unsandboxed engine, arbitrary code.

**`urllib` follows `file://` and `ftp://` too.** The helper you use to "fetch a URL" opens local files if you let it:

```python run
import tempfile
import urllib.request
from pathlib import Path

with tempfile.TemporaryDirectory() as tmp:
    secret = Path(tmp) / "secret.txt"
    secret.write_text("internal file contents")
    print(urllib.request.urlopen(secret.as_uri()).read().decode())             # as_uri() gives file:///tmp/...
```
```text
internal file contents
```

That is why SSRF checks start with `scheme == "https"` (section 14.6) and why the `requests`/`httpx` libraries, which only speak HTTP, are the safer choice for fetching.

**Other Python-specific items** to remember: `eval`, `exec` and `compile` on user input are remote code execution; `pickle`, `marshal` and `shelve` on untrusted data are too (section 14.7); `yaml.load` without `SafeLoader` as well; `tempfile.mktemp()` is racy, use `mkstemp()` or `NamedTemporaryFile`; `random` is not for secrets (section 15.4); `==` on secrets leaks timing (use `compare_digest`); mutable default arguments can leak state *between users' requests* in long-running servers; and global variables in a worker are shared by all users of that process, so never store the "current user" in a module-level variable (use request-scoped state).

### Try it: map the bug

Name the OWASP category for each: (a) an endpoint returns `403` when you ask for an invoice that exists and `404` when it does not; (b) a service loads a "plug-in" file uploaded by a user with `pickle`; (c) the app prints stack traces to users; (d) the team has no idea that the old `/v1` host is still running with a known bug.

<details><summary>Answer</summary>

(a) A01 broken access control (it also enables enumeration, an A07-style leak). (b) A08 software and data integrity failures (unsafe deserialisation; also arbitrary code execution, A03-like). (c) A05 security misconfiguration (verbose errors). (d) A06 outdated components or, in the API list, improper inventory management. Real bugs often fit several rows; the value of the list is that it makes you check all of them.

</details>


## 17. Project: security audit and hardening of an API

You now know the attacks and the defences. A real security review looks like this: you receive an application, you **find** what is wrong, you **prove** each finding with a failing test, you **fix** it, the test turns green, and you **report** what remains. This section does exactly that on the **Pagebound Orders API**, a small FastAPI service with users, orders, payments, an admin export, invoices, a logout redirect and a webhook tester. It works, and it is full of the kinds of mistakes this chapter described: 13 of them are planted.

The same method applies to the API project you built in swe.04, swe.05 or swe.06; section 17.11 gives you the checklist to audit it.

### 17.1 The system under review

Read it like an auditor: slowly, with the six questions of section 1.4 beside you. Try to find the flaws **before** you open the answer in 17.2.

```python
# shop_api.py
import hashlib
import jwt
import logging
import sqlite3
import traceback
import urllib.request
from pathlib import Path

from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse

SECRET = "secret"
log = logging.getLogger("shop")


def create_app(data_dir: str) -> FastAPI:
    app = FastAPI()
    db = sqlite3.connect(":memory:", check_same_thread=False)
    db.row_factory = sqlite3.Row
    db.executescript("""
        CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT UNIQUE, password_hash TEXT, role TEXT DEFAULT 'customer');
        CREATE TABLE orders (id INTEGER PRIMARY KEY, owner_id INTEGER, total_cents INTEGER, status TEXT DEFAULT 'pending',
                             note TEXT DEFAULT '');
        CREATE TABLE accounts (user_id INTEGER PRIMARY KEY, balance_cents INTEGER);
        CREATE TABLE payments (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, amount_cents INTEGER);
    """)
    app.state.db = db

    @app.exception_handler(Exception)
    async def on_error(request: Request, exc: Exception):
        return JSONResponse({"error": str(exc), "trace": traceback.format_exc()}, status_code=500)

    def current_user(authorization: str = Header(default="")):
        try:
            claims = jwt.decode(authorization.removeprefix("Bearer "), SECRET, algorithms=["HS256"])
        except jwt.PyJWTError:
            raise HTTPException(401, "invalid token")
        row = db.execute("SELECT id, name, role FROM users WHERE id = ?", (claims["sub"],)).fetchone()
        if row is None:
            raise HTTPException(401, "invalid token")
        return dict(row)

    @app.post("/register")
    def register(body: dict):
        digest = hashlib.sha256(body["password"].encode()).hexdigest()
        cur = db.execute("INSERT INTO users (name, password_hash) VALUES (?, ?)", (body["name"], digest))
        db.execute("INSERT INTO accounts VALUES (?, 100000)", (cur.lastrowid,))
        db.commit()
        return {"id": cur.lastrowid}

    @app.post("/login")
    def login(body: dict):
        row = db.execute("SELECT * FROM users WHERE name = ?", (body["name"],)).fetchone()
        if row is None:
            raise HTTPException(404, "no such user")
        if row["password_hash"] != hashlib.sha256(body["password"].encode()).hexdigest():
            log.warning("failed login for %s with password %s", body["name"], body["password"])
            raise HTTPException(401, "wrong password")
        return {"access_token": jwt.encode({"sub": str(row["id"]), "role": row["role"]}, SECRET, algorithm="HS256")}

    @app.post("/orders")
    def create_order(body: dict, user: dict = Depends(current_user)):
        cur = db.execute("INSERT INTO orders (owner_id, total_cents) VALUES (?, ?)", (user["id"], body["total_cents"]))
        db.commit()
        return {"id": cur.lastrowid}

    @app.get("/orders/search")
    def search_orders(q: str = "", sort: str = "id", user: dict = Depends(current_user)):
        sql = f"SELECT id, total_cents, status, note FROM orders WHERE owner_id = {user['id']} AND note LIKE '%{q}%' ORDER BY {sort}"
        return [dict(r) for r in db.execute(sql)]

    @app.get("/orders/{order_id}")
    def get_order(order_id: int, user: dict = Depends(current_user)):
        row = db.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
        if row is None:
            raise HTTPException(404, "order not found")
        return dict(row)

    @app.patch("/orders/{order_id}")
    def patch_order(order_id: int, body: dict, user: dict = Depends(current_user)):
        for column, value in body.items():
            db.execute(f"UPDATE orders SET {column} = ? WHERE id = ?", (value, order_id))
        db.commit()
        return dict(db.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone())

    @app.patch("/users/me")
    def update_me(body: dict, user: dict = Depends(current_user)):
        for column, value in body.items():
            if column in {"name", "role"}:
                db.execute(f"UPDATE users SET {column} = ? WHERE id = ?", (value, user["id"]))
        db.commit()
        return dict(db.execute("SELECT id, name, role FROM users WHERE id = ?", (user["id"],)).fetchone())

    @app.get("/admin/export")
    def export(user: dict = Depends(current_user)):
        return [dict(r) for r in db.execute("SELECT * FROM users")]

    @app.get("/invoices")
    def invoice(name: str, user: dict = Depends(current_user)):
        return FileResponse(Path(data_dir) / "invoices" / name)

    @app.post("/payments")
    def pay(body: dict, user: dict = Depends(current_user)):
        cur = db.execute("UPDATE accounts SET balance_cents = balance_cents - ? WHERE user_id = ? AND balance_cents >= ?",
                         (body["amount_cents"], user["id"], body["amount_cents"]))
        if cur.rowcount == 0:
            raise HTTPException(402, "insufficient funds")
        pid = db.execute("INSERT INTO payments (user_id, amount_cents) VALUES (?, ?)", (user["id"], body["amount_cents"])).lastrowid
        db.commit()
        return JSONResponse({"payment_id": pid}, status_code=201)

    @app.get("/logout")
    def logout(next: str = "/"):
        return RedirectResponse(next)

    @app.post("/webhooks/test")
    def webhook_test(body: dict, user: dict = Depends(current_user)):
        with urllib.request.urlopen(body["url"], timeout=3) as response:
            return {"status": "fetched", "preview": response.read(100).decode(errors="replace")}

    return app
```

A map of the endpoints makes a good first page of any audit: for each one, what does it protect, and which checks exist?

| Endpoint | Needs login? | Role check? | Ownership check? | Input model? | Money or side effect? |
|---|---|---|---|---|---|
| `POST /register` | no | n/a | n/a | free-form `dict` | creates a user and a balance |
| `POST /login` | no | n/a | n/a | free-form `dict` | issues a token |
| `POST /orders` | yes | no | n/a | free-form `dict` | creates an order |
| `GET /orders/search` | yes | no | yes (in SQL text) | query strings | none |
| `GET /orders/{id}` | yes | no | **no** | path int | none |
| `PATCH /orders/{id}` | yes | no | **no** | free-form `dict` | changes any column |
| `PATCH /users/me` | yes | no | n/a | free-form `dict` | changes name and role |
| `GET /admin/export` | yes | **no** | n/a | none | dumps the user table |
| `GET /invoices` | yes | no | no | query string | reads a file |
| `POST /payments` | yes | no | n/a | free-form `dict` | **moves money** |
| `GET /logout` | no | n/a | n/a | query string | redirects |
| `POST /webhooks/test` | yes | no | n/a | free-form `dict` | **fetches a URL** |

### 17.2 Work through the six questions

For every endpoint above, write down the answer to each question from section 1.4: *who is calling*, *may they do this to this object*, *is every input checked*, *what can this cost*, *what if it is called twice*, *what do we log and leak*. Also check the code that is not an endpoint: how tokens and passwords are made, how errors are reported, which settings are hard-coded.

### Try it: write your findings

Before you read on, spend ten minutes and write a list of every problem you can find, with a severity (critical, high, medium) and the OWASP category. Then compare.

<details><summary>Answer</summary>

| # | Finding | Where | Severity | OWASP | Section |
|---|---|---|---|---|---|
| 1 | The JWT secret is the word `"secret"` and tokens never expire | `SECRET`, `login` | critical | A02 / A07 | 4 |
| 2 | Passwords are stored as unsalted SHA-256 | `register`, `login` | high | A02 | 2 |
| 3 | Login says "no such user" or "wrong password" (account enumeration) | `login` | medium | A07 | 2.5 |
| 4 | Any user can read and edit any order (IDOR); `PATCH` also writes any column from the body | `get_order`, `patch_order` | critical | A01 / API1 | 8 |
| 5 | A user can set their own `role` (mass assignment) | `update_me` | critical | A01 / API3 | 8.5 |
| 6 | Any logged-in user can export the user table, including password hashes | `export` | critical | A01 / API5 | 7, 8.5 |
| 7 | SQL injection through `q` and `sort` | `search_orders` | critical | A03 | 14.3 |
| 8 | Path traversal in invoice downloads | `invoice` | high | A01 / A03 | 14.5 |
| 9 | No limit on login attempts | `login` | high | A07 / API4 | 11 |
| 10 | A repeated payment request charges twice | `pay` | high | A04 | 13 |
| 11 | Error responses include stack traces; the failed-login log contains the attempted password | `on_error`, `login` | medium | A05 / A09 | 15.6, 9.4 |
| 12 | Open redirect on logout | `logout` | medium | A01 | 14.8 |
| 13 | SSRF: the server fetches any URL, including `file://` and internal addresses | `webhook_test` | high | A10 | 14.6 |

Also missing: validation models on every body (a thread that runs through most findings), password policy, security headers, audit logging of important events, and HTTPS enforcement. Those become the "remaining risks" in 17.9.

</details>

### 17.3 Prove each finding with a test: red first

A finding without a test is an opinion. A test turns it into a **fact** and later into a **regression guard**. Each test below states the *correct* behaviour and carries a message naming the mistake, as the tests in this course do. The ones about permissions always include a check that the legitimate user still works, so that a server that rejects everything cannot pass.

```python
# test_audit.py
import logging
import os
import types

os.environ.setdefault("SHOP_JWT_SECRET", "test-only-secret-" + "x" * 32)       # the hardened app refuses to start without one

import jwt
import pytest
from fastapi.testclient import TestClient

import shop_api

PASSWORD = "correct horse battery"


@pytest.fixture
def world(tmp_path):
    (tmp_path / "invoices").mkdir()
    (tmp_path / "invoices" / "inv-1.txt").write_text("invoice one")
    (tmp_path / "secrets.txt").write_text("TOP SECRET")
    app = shop_api.create_app(str(tmp_path))
    client = TestClient(app, raise_server_exceptions=False)

    def signup(name, role=None):
        client.post("/register", json={"name": name, "password": PASSWORD})
        if role:
            app.state.db.execute("UPDATE users SET role = ? WHERE name = ?", (role, name))
            app.state.db.commit()
        token = client.post("/login", json={"name": name, "password": PASSWORD}).json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    return types.SimpleNamespace(client=client, app=app, db=app.state.db, signup=signup, dir=tmp_path)


def test_tokens_expire_and_use_a_strong_secret(world):
    token = world.signup("ada")["Authorization"].removeprefix("Bearer ")
    claims = jwt.decode(token, options={"verify_signature": False})
    assert "exp" in claims, "tokens must expire"
    with pytest.raises(jwt.PyJWTError):
        jwt.decode(token, "secret", algorithms=["HS256"])                      # a guessable key must not verify


def test_passwords_are_stored_with_a_slow_salted_hash(world):
    world.signup("ada")
    world.signup("bo")
    hashes = [r[0] for r in world.db.execute("SELECT password_hash FROM users ORDER BY id")]
    assert all(h.startswith("scrypt$") for h in hashes), "use a slow, salted password hash, not plain SHA-256"
    assert hashes[0] != hashes[1], "same password, different salt, different hash"


def test_login_does_not_reveal_which_usernames_exist(world):
    world.signup("ada")
    unknown = world.client.post("/login", json={"name": "nobody", "password": "x" * 12})
    wrong = world.client.post("/login", json={"name": "ada", "password": "wrong-password"})
    assert (unknown.status_code, unknown.json()) == (wrong.status_code, wrong.json()), "one message for every failure"


def test_orders_are_private_to_their_owner(world):
    ada, bo = world.signup("ada"), world.signup("bo")
    order = world.client.post("/orders", json={"total_cents": 500}, headers=ada).json()["id"]
    assert world.client.get(f"/orders/{order}", headers=ada).status_code == 200, "the owner must still get in"
    assert world.client.get(f"/orders/{order}", headers=bo).status_code == 404, "reading someone else's order"
    assert world.client.patch(f"/orders/{order}", json={"note": "hacked"}, headers=bo).status_code == 404, "editing it"
    assert world.client.get(f"/orders/{order}", headers=ada).json()["note"] == "", "the failed edit must change nothing"


def test_profile_update_cannot_change_the_role(world):
    ada = world.signup("ada")
    world.client.patch("/users/me", json={"name": "ada", "role": "admin"}, headers=ada)
    role = world.db.execute("SELECT role FROM users WHERE name = 'ada'").fetchone()[0]
    assert role == "customer", "a user must not be able to promote themselves"


def test_admin_export_is_for_admins_and_hides_hashes(world):
    ada, root = world.signup("ada"), world.signup("root", role="admin")
    assert world.client.get("/admin/export", headers=ada).status_code == 403, "a customer reached an admin endpoint"
    rows = world.client.get("/admin/export", headers=root)
    assert rows.status_code == 200
    assert "password_hash" not in rows.text, "never return password hashes, even to admins"


def test_search_resists_sql_injection(world):
    ada, bo = world.signup("ada"), world.signup("bo")
    world.client.post("/orders", json={"total_cents": 1}, headers=ada)
    bo_order = world.client.post("/orders", json={"total_cents": 2}, headers=bo).json()["id"]
    world.client.patch(f"/orders/{bo_order}", json={"note": "bo-private"}, headers=bo)
    legit = world.client.get("/orders/search", params={"q": "", "sort": "id"}, headers=ada)
    assert legit.status_code == 200 and len(legit.json()) == 1, "normal searching must keep working"
    attack = world.client.get("/orders/search", params={"q": "' OR owner_id = 2 OR note LIKE '"}, headers=ada)
    assert "bo-private" not in attack.text, "the q parameter is concatenated into SQL"
    for bad_sort in ("id; DROP TABLE orders", "(SELECT password_hash FROM users LIMIT 1)", "nonexistent"):
        r = world.client.get("/orders/search", params={"sort": bad_sort}, headers=ada)
        assert r.status_code in (400, 422), f"sort={bad_sort!r} must be refused, not passed to SQL"


def test_invoice_download_cannot_escape_its_folder(world):
    ada = world.signup("ada")
    assert world.client.get("/invoices", params={"name": "inv-1.txt"}, headers=ada).text == "invoice one"
    r = world.client.get("/invoices", params={"name": "../secrets.txt"}, headers=ada)
    assert "TOP SECRET" not in r.text, "path traversal out of the invoices folder"


def test_login_is_rate_limited(world):
    world.signup("ada")
    codes = [world.client.post("/login", json={"name": "ada", "password": f"guess-{i}-wrong"}).status_code for i in range(12)]
    assert 429 in codes, "twelve wrong passwords in a row were all processed"


def test_payment_is_safe_to_repeat(world):
    ada = world.signup("ada")
    headers = ada | {"Idempotency-Key": "pay-0001-ada"}
    first = world.client.post("/payments", json={"amount_cents": 1000}, headers=headers)
    again = world.client.post("/payments", json={"amount_cents": 1000}, headers=headers)
    assert first.status_code == again.status_code == 201
    assert first.json() == again.json(), "a retry must return the original payment"
    balance = world.db.execute("SELECT balance_cents FROM accounts WHERE user_id = 1").fetchone()[0]
    assert balance == 99_000, "the customer was charged twice"


def test_errors_do_not_leak_internals(world, monkeypatch):
    ada = world.signup("ada")
    r = world.client.post("/orders", json={"total_cents": [1, 2]}, headers=ada)
    assert "Traceback" not in r.text and "sqlite" not in r.text.lower(), "stack trace or SQL error shown to the client"
    monkeypatch.setattr(shop_api.jwt, "decode", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("db password=hunter2")))
    r = world.client.get("/orders/1", headers=ada)
    assert r.status_code == 500 and "hunter2" not in r.text, "unexpected errors must give a generic message"


def test_failed_login_does_not_log_the_password(world, caplog):
    world.signup("ada")
    with caplog.at_level(logging.DEBUG):
        world.client.post("/login", json={"name": "ada", "password": "Tr0ub4dor&3-typo"})
    assert "Tr0ub4dor&3-typo" not in caplog.text, "the attempted password was written to the log"


def test_logout_redirects_only_to_local_paths(world):
    for target, expected in [("/orders", "/orders"), ("https://evil.example", "/"), ("//evil.example", "/"), ("/\\evil.example", "/")]:
        r = world.client.get("/logout", params={"next": target}, follow_redirects=False)
        assert r.headers["location"] == expected, f"open redirect for next={target!r}"


def test_webhook_test_refuses_internal_and_file_urls(world, monkeypatch):
    ada = world.signup("ada")
    for url in [(world.dir / "secrets.txt").as_uri(), "http://127.0.0.1:9/", "https://127.0.0.1/", "https://169.254.169.254/"]:
        r = world.client.post("/webhooks/test", json={"url": url}, headers=ada)
        assert r.status_code == 400 and "TOP SECRET" not in r.text, f"server-side request forgery with {url}"

    class FakeResponse:
        def __enter__(self): return self
        def __exit__(self, *a): return False
        def read(self, n=-1): return b"hello from the partner"

    monkeypatch.setattr(shop_api.urllib.request, "urlopen", lambda *a, **k: FakeResponse())
    ok = world.client.post("/webhooks/test", json={"url": "https://93.184.216.34/hook"}, headers=ada)
    assert ok.status_code == 200, "a public https URL must still work"
```

Run them against the application as received:

```bash run
python -m pytest -q -p no:cacheprovider -W ignore --tb=no test_audit.py 2>&1 | tail -20
```
```text
FFFFFFFFFFFFFF                                                           [100%]
=========================== short test summary info ============================
FAILED test_audit.py::test_tokens_expire_and_use_a_strong_secret - AssertionE...
FAILED test_audit.py::test_passwords_are_stored_with_a_slow_salted_hash - Ass...
FAILED test_audit.py::test_login_does_not_reveal_which_usernames_exist - Asse...
FAILED test_audit.py::test_orders_are_private_to_their_owner - AssertionError...
FAILED test_audit.py::test_profile_update_cannot_change_the_role - AssertionE...
FAILED test_audit.py::test_admin_export_is_for_admins_and_hides_hashes - Asse...
FAILED test_audit.py::test_search_resists_sql_injection - AssertionError: the...
FAILED test_audit.py::test_invoice_download_cannot_escape_its_folder - Assert...
FAILED test_audit.py::test_login_is_rate_limited - AssertionError: twelve wro...
FAILED test_audit.py::test_payment_is_safe_to_repeat - AssertionError: a retr...
FAILED test_audit.py::test_errors_do_not_leak_internals - AssertionError: sta...
FAILED test_audit.py::test_failed_login_does_not_log_the_password - Assertion...
FAILED test_audit.py::test_logout_redirects_only_to_local_paths - AssertionEr...
FAILED test_audit.py::test_webhook_test_refuses_internal_and_file_urls - Asse...
14 failed in 1.40s
```

All 14 tests fail: that is the starting point of the audit, and it is a useful one. Each test names a hole, and we will close them one group at a time. (The tests are written once and then never change while we fix the code, which keeps us honest.)

### 17.4 Hardening, step A: foundations

First the building blocks that later fixes rely on: a **strong secret from the environment** that the app refuses to start without, a real **password hash**, **typed input models** with limits (and `extra="forbid"` where fields must not be added), the helper functions for safe redirects and for checking URLs, and a **generic error handler** that logs details instead of returning them. Each block below is shown as a before/after edit; lines starting with `-` were removed and lines starting with `+` were added.

```diff
# shop_api.py
- import hashlib
- import jwt
- import logging
- import sqlite3
- import traceback
- import urllib.request
- from pathlib import Path
-
- from fastapi import Depends, FastAPI, Header, HTTPException, Request
- from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
+ import base64
+ import hashlib
+ import hmac
+ import ipaddress
+ import logging
+ import os
+ import socket
+ import sqlite3
+ import threading
+ import time
+ import urllib.request
+ import uuid
+ from pathlib import Path
+ from urllib.parse import urlparse
+
+ import jwt
+ from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request
+ from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
+ from pydantic import BaseModel, ConfigDict, Field
```

```diff
# shop_api.py
- SECRET = "secret"
+ SECRET = os.environ.get("SHOP_JWT_SECRET", "")
+ if len(SECRET) < 32:
+     raise RuntimeError("SHOP_JWT_SECRET must be set to a random string of at least 32 characters")
+ TOKEN_LIFETIME = 900
```

```diff
# shop_api.py
- log = logging.getLogger("shop")
+ log = logging.getLogger("shop")
+
+
+ def hash_password(password: str) -> str:
+     salt = os.urandom(16)
+     digest = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1, maxmem=2**26)
+     return "scrypt$" + base64.b64encode(salt).decode() + "$" + base64.b64encode(digest).decode()
+
+
+ def verify_password(password: str, stored: str) -> bool:
+     try:
+         _, salt, digest = stored.split("$")
+         actual = hashlib.scrypt(password.encode(), salt=base64.b64decode(salt), n=2**14, r=8, p=1, maxmem=2**26)
+     except ValueError:
+         return False
+     return hmac.compare_digest(actual, base64.b64decode(digest))
+
+
+ DUMMY_HASH = hash_password("dummy password used so unknown users cost the same time")
```

```diff
# shop_api.py
-
-
- def create_app(data_dir: str) -> FastAPI:
+
+
+ class RegisterIn(BaseModel):
+     name: str = Field(min_length=2, max_length=64)
+     password: str = Field(min_length=10, max_length=256)
+
+
+ class LoginIn(BaseModel):
+     name: str = Field(max_length=64)
+     password: str = Field(max_length=256)
+
+
+ class OrderIn(BaseModel):
+     total_cents: int = Field(gt=0, le=1_000_000)
+
+
+ class NoteIn(BaseModel):
+     model_config = ConfigDict(extra="forbid")
+     note: str = Field(max_length=500)
+
+
+ class ProfileIn(BaseModel):
+     model_config = ConfigDict(extra="forbid")
+     name: str = Field(min_length=2, max_length=64)
+
+
+ class PaymentIn(BaseModel):
+     model_config = ConfigDict(extra="forbid")
+     amount_cents: int = Field(gt=0, le=1_000_000)
+
+
+ class UrlIn(BaseModel):
+     url: str = Field(max_length=2000)
+
+
+ def safe_next(target: str, default: str = "/") -> str:
+     if not target or "\\" in target or target.startswith("//") or not target.startswith("/"):
+         return default
+     parts = urlparse(target)
+     return default if parts.scheme or parts.netloc else target
+
+
+ def assert_public_https_url(url: str) -> None:
+     parts = urlparse(url)
+     if parts.scheme != "https" or not parts.hostname:
+         raise ValueError("only https URLs are allowed")
+     try:
+         addresses = [ipaddress.ip_address(parts.hostname)]
+     except ValueError:
+         addresses = [ipaddress.ip_address(info[4][0]) for info in socket.getaddrinfo(parts.hostname, parts.port or 443)]
+     for ip in addresses:
+         ip = getattr(ip, "ipv4_mapped", None) or ip
+         if not ip.is_global:
+             raise ValueError(f"{ip} is not a public address")
+
+
+ def create_app(data_dir: str) -> FastAPI:
```

```diff
# shop_api.py
-     app.state.db = db
+     app.state.db = db
+     failures: dict[tuple, list[float]] = {}            # recent failed logins per (name, client address)
+     payments_done: dict[tuple, tuple] = {}             # (user id, idempotency key) -> (fingerprint, response)
+     payment_lock = threading.Lock()
```

```diff
# shop_api.py
-
-     @app.exception_handler(Exception)
-     async def on_error(request: Request, exc: Exception):
-         return JSONResponse({"error": str(exc), "trace": traceback.format_exc()}, status_code=500)
+
+     @app.exception_handler(Exception)
+     async def on_error(request: Request, exc: Exception):
+         incident = uuid.uuid4().hex[:8]
+         log.exception("unhandled error, incident %s", incident)             # the details go to the log...
+         return JSONResponse({"error": "internal error", "incident": incident}, status_code=500)   # ...not the client
```

```bash run
python -m pytest -q -p no:cacheprovider -W ignore --tb=no test_audit.py 2>&1 | tail -20
```
```text
FFFFFFFFFF.FFF                                                           [100%]
=========================== short test summary info ============================
FAILED test_audit.py::test_tokens_expire_and_use_a_strong_secret - AssertionE...
FAILED test_audit.py::test_passwords_are_stored_with_a_slow_salted_hash - Ass...
FAILED test_audit.py::test_login_does_not_reveal_which_usernames_exist - Asse...
FAILED test_audit.py::test_orders_are_private_to_their_owner - AssertionError...
FAILED test_audit.py::test_profile_update_cannot_change_the_role - AssertionE...
FAILED test_audit.py::test_admin_export_is_for_admins_and_hides_hashes - Asse...
FAILED test_audit.py::test_search_resists_sql_injection - AssertionError: the...
FAILED test_audit.py::test_invoice_download_cannot_escape_its_folder - Assert...
FAILED test_audit.py::test_login_is_rate_limited - AssertionError: twelve wro...
FAILED test_audit.py::test_payment_is_safe_to_repeat - AssertionError: a retr...
FAILED test_audit.py::test_failed_login_does_not_log_the_password - Assertion...
FAILED test_audit.py::test_logout_redirects_only_to_local_paths - AssertionEr...
FAILED test_audit.py::test_webhook_test_refuses_internal_and_file_urls - Asse...
13 failed, 1 passed in 1.57s
```

The foundations are in place and nothing else changed yet: they only add tools and the generic error response (which already fixes the unexpected-error half of finding 11 and leaves the other tests as they were).

### 17.5 Step B: identity (findings 1, 2, 3, 9 and the log half of 11)

Passwords are hashed with the slow, salted function; tokens carry an expiry, are verified with required claims and the strong key; login answers with one message, always performs one hash check, is limited to five failures a minute per `(name, address)`, and never writes the password to the log.

```diff
# shop_api.py
-             claims = jwt.decode(authorization.removeprefix("Bearer "), SECRET, algorithms=["HS256"])
+             claims = jwt.decode(authorization.removeprefix("Bearer "), SECRET, algorithms=["HS256"],
+                                 options={"require": ["exp", "sub"]})
```

```diff
# shop_api.py
-     def register(body: dict):
-         digest = hashlib.sha256(body["password"].encode()).hexdigest()
-         cur = db.execute("INSERT INTO users (name, password_hash) VALUES (?, ?)", (body["name"], digest))
+     def register(body: RegisterIn):
+         cur = db.execute("INSERT INTO users (name, password_hash) VALUES (?, ?)", (body.name, hash_password(body.password)))
```

```diff
# shop_api.py
-     def login(body: dict):
-         row = db.execute("SELECT * FROM users WHERE name = ?", (body["name"],)).fetchone()
-         if row is None:
-             raise HTTPException(404, "no such user")
-         if row["password_hash"] != hashlib.sha256(body["password"].encode()).hexdigest():
-             log.warning("failed login for %s with password %s", body["name"], body["password"])
-             raise HTTPException(401, "wrong password")
-         return {"access_token": jwt.encode({"sub": str(row["id"]), "role": row["role"]}, SECRET, algorithm="HS256")}
+     def login(body: LoginIn, request: Request):
+         key, now = (body.name, request.client.host), time.monotonic()
+         recent = [t for t in failures.get(key, []) if now - t < 60]
+         if len(recent) >= 5:
+             raise HTTPException(429, "too many attempts, try again later", headers={"Retry-After": "60"})
+         row = db.execute("SELECT * FROM users WHERE name = ?", (body.name,)).fetchone()
+         ok = verify_password(body.password, row["password_hash"] if row else DUMMY_HASH)     # always one hash check
+         if row is None or not ok:
+             failures[key] = recent + [now]
+             log.warning("failed login for %s from %s", body.name, request.client.host)       # never the password
+             raise HTTPException(401, "invalid username or password")                          # one message for both cases
+         claims = {"sub": str(row["id"]), "iat": int(time.time()), "exp": int(time.time()) + TOKEN_LIFETIME}
+         return {"access_token": jwt.encode(claims, SECRET, algorithm="HS256")}
```

```bash run
python -m pytest -q -p no:cacheprovider -W ignore --tb=no test_audit.py 2>&1 | tail -20
```
```text
...FFFFF.F..FF                                                           [100%]
=========================== short test summary info ============================
FAILED test_audit.py::test_orders_are_private_to_their_owner - AssertionError...
FAILED test_audit.py::test_profile_update_cannot_change_the_role - AssertionE...
FAILED test_audit.py::test_admin_export_is_for_admins_and_hides_hashes - Asse...
FAILED test_audit.py::test_search_resists_sql_injection - AssertionError: the...
FAILED test_audit.py::test_invoice_download_cannot_escape_its_folder - Assert...
FAILED test_audit.py::test_payment_is_safe_to_repeat - AssertionError: a retr...
FAILED test_audit.py::test_logout_redirects_only_to_local_paths - AssertionEr...
FAILED test_audit.py::test_webhook_test_refuses_internal_and_file_urls - Asse...
8 failed, 6 passed in 4.18s
```

### 17.6 Step C: access control (findings 4, 5, 6)

The three kinds of authorisation: **object level** (queries scoped by the caller, `404` otherwise), **property level** (an input model that allows exactly one writable field), and **function level** (a role check, and an explicit column list so password hashes are never selected).

```diff
# shop_api.py
-     def create_order(body: dict, user: dict = Depends(current_user)):
-         cur = db.execute("INSERT INTO orders (owner_id, total_cents) VALUES (?, ?)", (user["id"], body["total_cents"]))
+     def create_order(body: OrderIn, user: dict = Depends(current_user)):
+         cur = db.execute("INSERT INTO orders (owner_id, total_cents) VALUES (?, ?)", (user["id"], body.total_cents))
```

```diff
# shop_api.py
-         row = db.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
-         if row is None:
-             raise HTTPException(404, "order not found")
-         return dict(row)
+         row = db.execute("SELECT * FROM orders WHERE id = ? AND owner_id = ?", (order_id, user["id"])).fetchone()
+         if row is None:
+             raise HTTPException(404, "order not found")                 # the same answer for "missing" and "not yours"
+         return dict(row)
```

```diff
# shop_api.py
-     def patch_order(order_id: int, body: dict, user: dict = Depends(current_user)):
-         for column, value in body.items():
-             db.execute(f"UPDATE orders SET {column} = ? WHERE id = ?", (value, order_id))
-         db.commit()
-         return dict(db.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone())
+     def patch_order(order_id: int, body: NoteIn, user: dict = Depends(current_user)):
+         cur = db.execute("UPDATE orders SET note = ? WHERE id = ? AND owner_id = ?", (body.note, order_id, user["id"]))
+         db.commit()
+         if cur.rowcount == 0:
+             raise HTTPException(404, "order not found")
+         return dict(db.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone())
```

```diff
# shop_api.py
-     def update_me(body: dict, user: dict = Depends(current_user)):
-         for column, value in body.items():
-             if column in {"name", "role"}:
-                 db.execute(f"UPDATE users SET {column} = ? WHERE id = ?", (value, user["id"]))
-         db.commit()
+     def update_me(body: ProfileIn, user: dict = Depends(current_user)):
+         db.execute("UPDATE users SET name = ? WHERE id = ?", (body.name, user["id"]))      # only the name is writable
+         db.commit()
```

```diff
# shop_api.py
-     def export(user: dict = Depends(current_user)):
-         return [dict(r) for r in db.execute("SELECT * FROM users")]
+     def export(user: dict = Depends(current_user)):
+         if user["role"] != "admin":
+             raise HTTPException(403, "admins only")
+         return [dict(r) for r in db.execute("SELECT id, name, role FROM users")]           # no password hashes
```

```bash run
python -m pytest -q -p no:cacheprovider -W ignore --tb=no test_audit.py 2>&1 | tail -20
```
```text
......FF.F..FF                                                           [100%]
=========================== short test summary info ============================
FAILED test_audit.py::test_search_resists_sql_injection - AssertionError: the...
FAILED test_audit.py::test_invoice_download_cannot_escape_its_folder - Assert...
FAILED test_audit.py::test_payment_is_safe_to_repeat - AssertionError: a retr...
FAILED test_audit.py::test_logout_redirects_only_to_local_paths - AssertionEr...
FAILED test_audit.py::test_webhook_test_refuses_internal_and_file_urls - Asse...
5 failed, 9 passed in 4.72s
```

### 17.7 Step D: injection and files (findings 7, 8)

Values become query parameters and the sort field passes through an allow-list. File names are resolved and compared with the folder before use.

```diff
# shop_api.py
-     def search_orders(q: str = "", sort: str = "id", user: dict = Depends(current_user)):
-         sql = f"SELECT id, total_cents, status, note FROM orders WHERE owner_id = {user['id']} AND note LIKE '%{q}%' ORDER BY {sort}"
-         return [dict(r) for r in db.execute(sql)]
+     def search_orders(q: str = Query("", max_length=100), sort: str = "id", user: dict = Depends(current_user)):
+         column = {"id": "id", "total": "total_cents", "status": "status"}.get(sort)      # allow-list of sortable fields
+         if column is None:
+             raise HTTPException(422, "sort must be one of: id, total, status")
+         sql = f"SELECT id, total_cents, status, note FROM orders WHERE owner_id = ? AND note LIKE ? ORDER BY {column}"
+         return [dict(r) for r in db.execute(sql, (user["id"], f"%{q}%"))]               # values are parameters
```

```diff
# shop_api.py
-         return FileResponse(Path(data_dir) / "invoices" / name)
+         base = (Path(data_dir) / "invoices").resolve()
+         target = (base / name).resolve()
+         if not target.is_relative_to(base) or not target.is_file():                         # resolve first, then compare
+             raise HTTPException(404, "invoice not found")
+         return FileResponse(target)
```

```bash run
python -m pytest -q -p no:cacheprovider -W ignore --tb=no test_audit.py 2>&1 | tail -20
```
```text
.........F..FF                                                           [100%]
=========================== short test summary info ============================
FAILED test_audit.py::test_payment_is_safe_to_repeat - AssertionError: a retr...
FAILED test_audit.py::test_logout_redirects_only_to_local_paths - AssertionEr...
FAILED test_audit.py::test_webhook_test_refuses_internal_and_file_urls - Asse...
3 failed, 11 passed in 4.37s
```

### 17.8 Step E: money, redirects and outgoing requests (findings 10, 12, 13)

The payment endpoint requires an `Idempotency-Key` and replays the stored result; the logout accepts only local paths; the webhook tester refuses anything but public `https` addresses.

```diff
# shop_api.py
-     def pay(body: dict, user: dict = Depends(current_user)):
-         cur = db.execute("UPDATE accounts SET balance_cents = balance_cents - ? WHERE user_id = ? AND balance_cents >= ?",
-                          (body["amount_cents"], user["id"], body["amount_cents"]))
-         if cur.rowcount == 0:
-             raise HTTPException(402, "insufficient funds")
-         pid = db.execute("INSERT INTO payments (user_id, amount_cents) VALUES (?, ?)", (user["id"], body["amount_cents"])).lastrowid
-         db.commit()
-         return JSONResponse({"payment_id": pid}, status_code=201)
+     def pay(body: PaymentIn, user: dict = Depends(current_user),
+             idempotency_key: str = Header(min_length=8, max_length=64)):
+         with payment_lock:       # in-memory and per-process; section 13 shows the database version that works across servers
+             cached = payments_done.get((user["id"], idempotency_key))
+             if cached is not None:
+                 if cached[0] != body.amount_cents:
+                     raise HTTPException(422, "this Idempotency-Key was used with a different request")
+                 return JSONResponse(cached[1], status_code=201, headers={"Idempotent-Replayed": "true"})
+             cur = db.execute("UPDATE accounts SET balance_cents = balance_cents - ? WHERE user_id = ? AND balance_cents >= ?",
+                              (body.amount_cents, user["id"], body.amount_cents))
+             if cur.rowcount == 0:
+                 raise HTTPException(402, "insufficient funds")
+             pid = db.execute("INSERT INTO payments (user_id, amount_cents) VALUES (?, ?)", (user["id"], body.amount_cents)).lastrowid
+             db.commit()
+             payments_done[(user["id"], idempotency_key)] = (body.amount_cents, {"payment_id": pid})
+             return JSONResponse({"payment_id": pid}, status_code=201)
```

```diff
# shop_api.py
-         return RedirectResponse(next)
+         return RedirectResponse(safe_next(next))
```

```diff
# shop_api.py
-     def webhook_test(body: dict, user: dict = Depends(current_user)):
-         with urllib.request.urlopen(body["url"], timeout=3) as response:
+     def webhook_test(body: UrlIn, user: dict = Depends(current_user)):
+         try:
+             assert_public_https_url(body.url)
+         except (ValueError, OSError) as exc:
+             raise HTTPException(400, f"url refused: {exc}")
+         with urllib.request.urlopen(body.url, timeout=3) as response:
```

```bash run
python -m pytest -q -p no:cacheprovider -W ignore --tb=no test_audit.py 2>&1 | tail -20
```
```text
..............                                                           [100%]
14 passed in 4.52s
```

All 14 tests pass. A passing test suite is only as good as its ability to fail, so we checked that too: we re-introduced fifteen realistic regressions into the hardened code, one at a time, and ran the suite after each. All fifteen were caught.

| Regression put back | Caught by |
|---|---|
| token without `exp` | the token test (and many others, since nothing can log in) |
| plain SHA-256 password hash | the password-hash test |
| login answers "no such user" | the enumeration test |
| order lookup without the owner filter | the privacy test |
| order update without the owner filter | the privacy test (it checks the data afterwards) |
| `role` writable in the profile | the role test |
| admin check removed | the admin test |
| `sort` pasted into SQL | the injection test |
| path traversal check removed | the invoice test |
| rate limit raised to 5,000 | the rate-limit test |
| idempotency lookup disabled | the payment test |
| error handler returns `str(exc)` | the error-leak test |
| password written to the log | the log test |
| redirect target unchecked | the redirect test |
| URL check removed | the webhook test |

(We did this with a small script that replaced one line of `shop_api.py` per run. Doing the same to your own tests is how you learn that they protect something, as in core.08 and core.19.)

### 17.9 Remaining risks: the honest part of a report

Hardening is never finished. A good report lists what was **not** fixed and why:

| Remaining risk | Why it remains | Next step |
|---|---|---|
| Rate limit and idempotency state are in memory | work in one process only; lost on restart | move to Redis or the database (sections 11.6, 13.4; swe.08) |
| The SSRF check validates the first hop only | redirects and DNS rebinding can still reach internal hosts | connect to the validated IP, disable redirects, restrict outgoing network access |
| Access tokens cannot be revoked before they expire (15 minutes) | stateless JWT | refresh tokens with rotation and a deny-list (section 4.4) |
| No audit log of security events | only warnings are logged | structured JSON logs with request ids, shipped off-box (section 15.6) |
| No security headers, no HTTPS redirect | not part of the application code | middleware (section 14.9) and proxy settings |
| No password policy beyond length, no MFA | scope | breached-password check, TOTP (sections 2.4, 6.3) |
| Dependencies not scanned | no network here | `pip-audit` in CI (section 15.8) |
| Roles are one string; no fine-grained permissions | simplicity | the policy function of section 7.3 |

### 17.10 The audit report template

Keep reports short and testable. One row per finding:

| ID | Title | Severity | Evidence | Fix | Test | Status |
|---|---|---|---|---|---|---|
| F-04 | Any user can read or edit any order | critical | user `bo` reads order 1 of `ada` with a valid token | scope the query by `owner_id`, return 404 | `test_orders_are_private_to_their_owner` | fixed |

with an executive summary at the top (how many findings by severity, what was fixed, what remains) and the remaining-risk table below. Severity combines **how easy** the exploit is, **how much** it exposes, and **how many** users it touches.

### 17.11 Your turn: audit your own API project

The module project asks you to audit and harden the API you built earlier (the Flask blog of swe.04, the FastAPI TaskFlow of swe.05, the Django inventory app of swe.06, or a project of your own). Work through it like this:

1. **Inventory:** list every route, with method, auth, role and object checks, input model, and side effects (a table like 17.1). List secrets and where they come from. List dependencies.
2. **Ask the six questions** for each route.
3. **Write failing tests first** for each finding, using the patterns of this chapter: two-actor ownership tests, mass-assignment tests, a route-coverage meta-test (section 8.4), injection payloads, rate-limit and idempotency tests.
4. **Fix** one finding at a time and keep the tests green.
5. **Run tools** (below), read their output with judgement, and triage false positives.
6. **Write the report**: findings, fixes, tests, remaining risk.

A checklist to keep beside you:

- [ ] Authentication on by default; public routes listed in one place.
- [ ] Passwords: slow salted hash, length limits, generic login errors, throttling, breached-password check.
- [ ] Sessions or tokens: `HttpOnly`/`Secure`/`SameSite` cookies or short tokens with `exp`, `aud`, pinned algorithms; fresh session id on login; logout destroys server state.
- [ ] Every object lookup scoped by the caller; every privileged route role-checked; separate input and output models.
- [ ] Every list paginated with a maximum; sort and filter fields on allow-lists.
- [ ] No string-built SQL, no `shell=True`, no `pickle`/`yaml.load` on outside data, file paths resolved and checked, outgoing URLs restricted.
- [ ] Money and stock changes are atomic and idempotent; concurrent updates use `UPDATE ... WHERE` or `If-Match`.
- [ ] Rate limits on login, reset and expensive routes; body size limits; timeouts.
- [ ] Secrets in the environment or a secret manager, none in git (scanner in CI); `DEBUG` off; docs endpoints reviewed; CORS reviewed.
- [ ] Errors generic with incident ids; logs have security events and no secrets; logs are shipped off the server.
- [ ] Dependencies pinned and scanned; unused ones removed.

> **Try it on your machine**: automatic scanners find some of these problems. They are noisy, so read each result.
>
> ```bash
> pip install bandit pip-audit
> bandit -r . -ll          # static analysis for common Python security smells (shell=True, pickle, weak hashes, ...)
> pip-audit                 # known vulnerabilities in your installed dependencies
> ```
>
> Expected: `bandit` prints a list of issues with a severity, a confidence and a line number for each (the planted `hashlib.sha256` password hashing, `urllib` with `file:` support and similar usually show up); `pip-audit` prints a table of vulnerable packages or says that no known vulnerabilities were found. Scanners do not understand your business rules: no tool will tell you that user `bo` can read user `ada`'s order. Only a two-actor test does.

## 18. Common traps

1. **Authenticating but not authorising.** A valid token is not permission (7, 8).
2. **Looking up objects by id alone** instead of "id within the caller's scope" (8.3).
3. **Testing security with one user.** Ownership bugs need two actors, and a check that the owner still works (8.4).
4. **Returning `403` for objects that belong to others**, which confirms they exist (7.5).
5. **Accepting whatever fields arrive** (`role`, `owner_id`, `price`) and returning whole database rows (8.5).
6. **Treating random ids as access control.** They only reduce guessing (8.2).
7. **Fast hashes for passwords** (SHA-256, MD5), no salt, or a hash scheme you invented (2).
8. **Distinct messages or timings for unknown users** (2.5).
9. **Accepting JWTs without pinning the algorithm, checking `exp`, `aud` and `iss`**, or using a short, guessable secret (4).
10. **Tokens in `localStorage`**; very long-lived access tokens; refresh tokens without rotation (3, 4).
11. **Session id kept across login** (fixation) or logout that only deletes the browser cookie (3.3, 3.4).
12. **Loose `redirect_uri` matching, missing `state`, no PKCE** in OAuth2; linking accounts by an unverified e-mail (5).
13. **Comparing secrets with `==`**; using `random` for tokens (15.4).
14. **Hard locking accounts after N failures**, which lets attackers lock out customers (11.5).
15. **Trusting `X-Forwarded-For`** for rate limits, or in-memory limits behind several workers (11).
16. **Fixed-window counters** that allow double the limit at the boundary (11.2).
17. **Offset pagination on large, changing tables** and unbounded lists; `?sort=` or `?filter=` on any column (10).
18. **Read-then-write** instead of one atomic `UPDATE ... WHERE` for balances, stock and versions (12.6, 13).
19. **Retrying a `POST` without an idempotency key**, or generating a new key per attempt (13).
20. **String-built SQL, `shell=True`, `pickle.loads`, `yaml.load`, `eval`** on outside data (14).
21. **`name.startswith(base)` or `".." in name` for path checks** instead of resolve-then-compare (14.5).
22. **Fetching user-supplied URLs** without scheme, address and redirect checks (14.6).
23. **`assert` as a permission check**; it disappears under `python -O` (16.1).
24. **Secrets in git, in logs, in URLs or in error messages** (15).
25. **Debug mode, stack traces or open `/docs` in production** (9.4, 15.7).
26. **No inventory of versions, hosts and routes**; old versions without the new fixes (12.5).
27. **Security through a scanner only.** Tools find patterns; tests prove your rules (17).

## 19. Collected traps

| If you see... | The cause is usually... | Look at |
|---|---|---|
| a user can read another user's data by changing an id | missing ownership check (IDOR/BOLA) | 8 |
| `403` for other people's objects, `404` for missing ones | existence leak | 7.5 |
| a customer reaches `/admin/...` | missing function-level check | 7, 8.5 |
| a user turns into an admin after a `PATCH` | mass assignment | 8.5 |
| `401` with no `WWW-Authenticate` header | incomplete token challenge | 4.5 |
| `jwt.exceptions.MissingRequiredClaimError` | `exp`/`sub`/`aud` required but not issued | 4.2 |
| `InvalidAlgorithmError` | token or key uses another algorithm than the verifier allows | 4.3 |
| the same cookie works after logout | session not destroyed on the server | 3.4 |
| login works without a fresh session id | fixation | 3.3 |
| `ValueError: [digital envelope routines] memory limit exceeded` | scrypt needs `maxmem` | 2.2 |
| two charges after a timeout | no idempotency key | 13 |
| `409` on a retry with the same key | the first request is still running; retry after `Retry-After` | 13.3 |
| `422` on a retry with the same key | key reused with a different body | 13.3 |
| `412` / `428` on update | `If-Match` stale or missing | 12.6 |
| items repeated or missing between pages | offset pagination on a changing table | 10.2 |
| `429` with `Retry-After` | rate limit; the client must back off | 11.4 |
| rate limit never triggers behind a proxy | keyed on a spoofable header, or per-process counters | 11.3, 11.6 |
| a stack trace in a response | catch-all handler missing, debug on | 9.4, 15.7 |
| a password or token in the logs | logging request bodies or exceptions without redaction | 15.6 |
| `sqlite3.OperationalError: near ...` from a search box | string-built SQL | 14.3 |
| `/etc/passwd` or `.env` content in a response | path traversal | 14.5 |
| requests to `169.254.169.254` or `localhost` from your server | SSRF | 14.6 |
| a redirect to another domain after login | open redirect | 14.8 |
| permission check ignored in production | `assert` removed by `-O` | 16.1 |

## 20. Summary

- **Think like an attacker.** Everything from the network is untrusted. Ask six questions for every endpoint: who is calling, may they do this to this object, is every input checked, what can it cost, what if it is repeated, what do we log and leak. STRIDE helps to find the threats; deny by default, least privilege and defence in depth are the habits.
- **Passwords:** slow, salted, memory-hard hashes with the parameters stored in the hash and a rehash-on-login upgrade path; constant-time compares; generic login errors with one dummy hash check; length rules instead of composition rules; single-use, short-lived, hashed reset tokens.
- **Sessions and cookies:** random server-side ids, `HttpOnly`, `Secure`, `SameSite`; new id at login; real logout; idle and absolute timeouts; CSRF defences (SameSite, tokens, Origin checks).
- **Tokens:** JWTs are signed, not secret; pin the algorithm and require `exp`, `aud`, `iss`; use strong keys; short access tokens plus rotating refresh tokens with reuse detection; neither sessions nor JWT is simply "better".
- **OAuth2/OIDC:** authorization code with PKCE; exact `redirect_uri` and `state`; scopes enforced by the resource server; the ID token proves who logged in, the access token does not; never link accounts by an unverified e-mail.
- **API keys, TOTP, signed webhooks:** hashed keys with prefixes and scopes; TOTP with replay protection; HMAC signatures with timestamps and event ids.
- **Authorisation:** function, object and property level; one deny-by-default policy; scope queries by the caller; `404` for objects that are not yours. **Test with two actors** and with a route-coverage meta-test.
- **API design:** resources and methods with the right safety and idempotency; accurate status codes; one error format that never leaks; money in integers; cursor pagination, allow-listed filters and sort, bounded lists; versions with deprecation headers and contract tests; `ETag`/`If-Match` against lost updates.
- **Abuse protection:** token buckets or sliding windows keyed on the right identity, `429` with `Retry-After`, body-size limits, throttle rather than lock accounts, shared stores for several workers.
- **Idempotency keys:** claim the key with a unique constraint, store a request fingerprint, make the work and the stored result one transaction, replay stored responses, return `409` for in-flight duplicates; clients reuse one key per operation with backoff and jitter.
- **Validation and injection:** allow-lists at the boundary; parameterised SQL; argument lists instead of shells; resolve-then-compare paths; no unsafe deserialisation; public-HTTPS-only outgoing fetches; local-only redirects; security headers.
- **Secrets, logs, dependencies:** secrets from the environment or a secret manager, never in git or logs; fail fast on weak config; `secrets` instead of `random`; structured, redacted audit logging; pinned and scanned dependencies.
- **The OWASP lists** are a map; the **audit method** (inventory, six questions, failing tests, fixes, mutation check, remaining risks, report) is what you repeat on every real system.

Next: the 35 problems for this module practise reading and exploiting vulnerable snippets, writing two-actor tests, hashing and token handling, designing safe REST endpoints, building rate limiters and idempotent handlers, and hardening small APIs.
