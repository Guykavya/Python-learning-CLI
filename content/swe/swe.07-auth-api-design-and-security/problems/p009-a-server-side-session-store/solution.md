## Approach

```python
class SessionStore:
    def __init__(self, clock, idle=30 * 60, absolute=8 * 3600):
        self.clock, self.idle, self.absolute = clock, idle, absolute
        self.rows = {}            # session id -> {"user", "created", "seen"}

    def _live(self, sid):
        row = self.rows.get(sid) if isinstance(sid, str) else None
        if row is None:
            return None
        now = self.clock()
        if now - row["seen"] >= self.idle or now - row["created"] >= self.absolute:
            del self.rows[sid]
            return None
        return row

    def create(self, user):
        sid = secrets.token_urlsafe(32)
        now = self.clock()
        self.rows[sid] = {"user": user, "created": now, "seen": now}
        return sid

    def get(self, sid):
        row = self._live(sid)
        if row is None:
            return None
        row["seen"] = self.clock()
        return row["user"]

    def rotate(self, old_sid, user=None):
        row = self._live(old_sid)
        if row is None:
            return None
        del self.rows[old_sid]
        sid = secrets.token_urlsafe(32)
        self.rows[sid] = {"user": row["user"] if user is None else user,
                          "created": row["created"], "seen": self.clock()}
        return sid

    def destroy(self, sid):
        if isinstance(sid, str):
            self.rows.pop(sid, None)
```

Ideas from the chapter:

- **Two timers (3.4).** The idle timer limits what a forgotten, open browser allows; the absolute timer limits what a *stolen* cookie allows, because an attacker who keeps using it would otherwise keep it alive for ever.
- **A fresh id at login (3.3).** In a *session fixation* attack the attacker plants a known id in the victim's browser and waits for the login. If the login only adds the user to the existing session, the attacker's id now means "the victim". `rotate` kills the old id, so the planted one is useless.
- **Rotation must not reset the absolute clock**, or a caller (or an attacker who can trigger rotations) could keep a session alive for ever.
- **One `_live` helper** makes the boundary rule (`>=`) exist in exactly one place; this is what the "fixed clock" test of chapter 3 checks.
- **Server-side state** means logout really works: `destroy` removes the row, so a copied cookie is dead too.

## Complexity

All four operations are `O(1)` on average (dictionary operations). Memory grows with the number of live sessions; a real store also removes expired rows in a background job, because rows of users who never come back are only deleted when somebody tries their id.

## Another way

Store sessions in the database (or Redis, with a key expiry equal to the idle time) so several app servers share them and restarts do not log everybody out. The rules stay the same. Chapter 3 notes the alternative of **signed-cookie sessions**: no server state, but "log out everywhere" and early revocation need extra work.
