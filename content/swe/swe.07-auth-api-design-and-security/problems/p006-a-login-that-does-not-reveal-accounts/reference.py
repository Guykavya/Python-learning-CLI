DUMMY_HASH = "dummy-hash-for-timing"


class LoginFailed(Exception):
    """Raised for every failed login, with the same message."""


def login(users: dict[str, str], username: str, password: str, verify) -> str:
    stored = users.get(username)
    known = stored is not None
    ok = verify(password, stored if known else DUMMY_HASH)     # always exactly one verification
    if known and ok:
        return username
    raise LoginFailed("invalid username or password")          # one message for every failure
