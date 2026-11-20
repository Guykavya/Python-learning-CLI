import secrets


class SessionStore:
    def __init__(self, clock, idle: int = 30 * 60, absolute: int = 8 * 3600):
        self.clock = clock
        self.idle = idle
        self.absolute = absolute
        self.rows = {}            # TODO: session id -> what you need to remember

    def create(self, user: str) -> str:
        # TODO: new id with secrets.token_urlsafe(32), remember user, created and last-seen times
        return ""

    def get(self, sid):
        # TODO: user name or None; slide the idle timer; delete expired sessions
        return None

    def rotate(self, old_sid, user=None):
        # TODO: destroy old_sid, return a new id (same creation time), or None if old_sid is not live
        return None

    def destroy(self, sid) -> None:
        # TODO: forget the session; unknown ids and None are fine
        pass
