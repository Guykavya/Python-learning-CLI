import secrets


class SessionStore:
    def __init__(self, clock, idle: int = 30 * 60, absolute: int = 8 * 3600):
        self.clock = clock
        self.idle = idle
        self.absolute = absolute
        self.rows = {}            # session id -> {"user", "created", "seen"}

    def _live(self, sid):
        """Return the row of a live session (and slide nothing), or None. Expired rows are deleted."""
        row = self.rows.get(sid) if isinstance(sid, str) else None
        if row is None:
            return None
        now = self.clock()
        if now - row["seen"] >= self.idle or now - row["created"] >= self.absolute:
            del self.rows[sid]
            return None
        return row

    def _new_id(self):
        while True:
            sid = secrets.token_urlsafe(32)
            if sid not in self.rows:
                return sid

    def create(self, user: str) -> str:
        sid = self._new_id()
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
        sid = self._new_id()
        self.rows[sid] = {"user": row["user"] if user is None else user,
                          "created": row["created"], "seen": self.clock()}
        return sid

    def destroy(self, sid) -> None:
        if isinstance(sid, str):
            self.rows.pop(sid, None)
