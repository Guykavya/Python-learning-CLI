## Model answer

**1. The three parts.** `payload.timestamp.signature`.
The payload `eyJyb2xlIjoibWVtYmVyIiwidXNlcl9pZCI6N30` is Base64-URL for the JSON `{"role":"member","user_id":7}`. The second part `av7iBw` is the time the cookie was signed, as a number of seconds (Base64-encoded); Flask uses it to reject a cookie older than `PERMANENT_SESSION_LIFETIME`. The third part is the **signature**: an HMAC of the first two parts, computed with `SECRET_KEY`.

**2. Signed, not encrypted.** Anyone who has the cookie can **read** the payload with a few lines of code, so a session must never hold secrets (a password, a card number). Nobody can **change** the payload without the key: if the user edits `user_id` from 7 to 1, the signature no longer matches and Flask treats the session as empty. The user can still **copy** the cookie (anyone who steals it can replay it until it expires), and can delete it.

**3. A leaked or weak key.** The signature is the only protection. With the key, an attacker can compute a valid signature for any payload, for example `{"user_id": 1}`, and **forge** a session for any user without a password. A short guessable key (`"dev"`) can be found by trying words against one real cookie. So the key must be long, random, secret, different per environment, and rotating it logs everyone out.

**4. Only a user id.** The payload is readable and lives in the browser: a role or a price stored there is *visible* and, if the key ever leaks, *changeable*. More importantly it goes stale: if an admin loses the role at noon, a cookie issued in the morning still says `admin`. Keep only the id and load the user and the permissions from the database on **every** request.

**5. `session.clear()` at login.** In **session fixation** the attacker gets the victim to use a session the attacker already knows (for example by planting a cookie before login). If the login only *adds* `user_id` to that session, the attacker's copy of the cookie becomes a logged-in session. Clearing first discards everything the old session carried, so the login starts a fresh one (which is why a CSRF token must be created again after login).

**Checklist: your answer should mention**
- [ ] payload decoded: `{"role": "member", "user_id": 7}`
- [ ] second part = timestamp, third = signature (HMAC with the secret key)
- [ ] signed means **readable but not changeable** (no secrets inside)
- [ ] the user can still copy/replay the cookie
- [ ] leaked or weak key lets an attacker **forge** any session
- [ ] store only the user id and look the user up each request (roles change, data goes stale)
- [ ] `session.clear()` at login prevents **session fixation**
