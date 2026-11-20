# A stored hash for a user that does not exist. In the real app it is made once at start-up:
#   DUMMY_HASH = hash_password("dummy-password-for-timing")
DUMMY_HASH = "dummy-hash-for-timing"


class LoginFailed(Exception):
    """Raised for every failed login, with the same message."""


def login(users: dict[str, str], username: str, password: str, verify) -> str:
    # TODO: one verify() call per attempt (DUMMY_HASH for unknown users), one message for every failure
    return username
