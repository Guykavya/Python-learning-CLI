import jwt

SECRET = "demo-secret-" + "k" * 40          # in a real app: from the environment (section 18)
ALGORITHM = "HS256"


class InvalidToken(Exception):
    """Any problem with a token: expired, forged, malformed."""


def make_token(user_id: int, now: int, minutes: int = 15) -> str:
    # TODO: sub (as a string) and exp, signed with SECRET and HS256
    return ""


def read_token(token: str, now: int) -> int:
    # TODO: decode, check exp against now, convert every problem into InvalidToken
    return 0
