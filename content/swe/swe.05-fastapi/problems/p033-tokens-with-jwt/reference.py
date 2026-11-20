import jwt

SECRET = "demo-secret-" + "k" * 40          # in a real app: from the environment (section 18)
ALGORITHM = "HS256"


class InvalidToken(Exception):
    """Any problem with a token: expired, forged, malformed."""


def make_token(user_id: int, now: int, minutes: int = 15) -> str:
    claims = {"sub": str(user_id), "exp": now + minutes * 60}
    return jwt.encode(claims, SECRET, algorithm=ALGORITHM)


def read_token(token: str, now: int) -> int:
    try:
        payload = jwt.decode(
            token, SECRET, algorithms=[ALGORITHM],
            options={"verify_exp": False, "require": ["sub", "exp"]},   # we check exp with OUR clock
        )
    except jwt.PyJWTError as exc:
        raise InvalidToken(str(exc)) from exc
    if not isinstance(payload["exp"], int) or now >= payload["exp"]:
        raise InvalidToken("Token expired")
    try:
        return int(payload["sub"])
    except ValueError as exc:
        raise InvalidToken("Bad subject") from exc
