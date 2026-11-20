# A server-side session store

Chapter sections 3.2 (a server-side session store), 3.3 (session fixation) and 3.4 (logout and timeouts), and "Try it: a fixed clock". Write the object a login system keeps in memory: it hands out session ids, forgets them when they expire and replaces them when the user's rights change.

```python
class SessionStore:
    def __init__(self, clock, idle: int = 30 * 60, absolute: int = 8 * 3600): ...
    def create(self, user: str) -> str: ...
    def get(self, sid: str | None) -> str | None: ...
    def rotate(self, old_sid: str, user: str | None = None) -> str | None: ...
    def destroy(self, sid: str | None) -> None: ...
```

- `clock()` returns the current time in seconds (given; the test moves a fake one; never call `time`).
- **`create(user)`** returns a new session id made with `secrets.token_urlsafe(32)` (43 characters, never a counter or the user name).
- **`get(sid)`** returns the **user name** of a live session, and `None` for a missing, unknown or expired session. Two timers apply:
  - **idle:** a session expires when `idle` seconds passed since it was **last used**;
  - **absolute:** a session expires when `absolute` seconds passed since it was **created**, however active it was.
  - A session is expired as soon as the elapsed time **is equal to or greater than** the limit (at exactly 1800 s idle it is already dead).
  - A successful `get` **slides** the idle timer (it counts as "used now"). A failed `get` changes nothing, and an expired session is deleted.
- **`rotate(old_sid, user=None)`** is for login and privilege changes (session fixation, chapter 3.3): it **destroys** `old_sid` and returns a **new** id. The new session keeps the user of the old one, or gets `user` if it is given (this is how an anonymous pre-login session becomes a logged-in one). The new session starts with a fresh idle timer but **inherits the original creation time**, so rotating can never extend the absolute limit. If `old_sid` is not a live session, return `None` and create nothing.
- **`destroy(sid)`** deletes the session (logout). Destroying an unknown id or `None` is not an error.

## Example

```text
clock = [0]; store = SessionStore(lambda: clock[0])
sid = store.create("asha")
clock[0] = 1799; store.get(sid)   -> "asha"     (and the idle timer restarts at 1799)
clock[0] = 3598; store.get(sid)   -> "asha"     (1799 s since last use)
clock[0] = 5397; store.get(sid)   -> "asha"
...kept active every 1000 s... at clock 28800 -> None   (absolute limit, even though active)

anon = store.create("anonymous")
new = store.rotate(anon, user="asha")     # login: old id dies, the new id belongs to asha
store.get(anon)                           -> None
store.get(new)                            -> "asha"
```

The tests import `SessionStore`.
