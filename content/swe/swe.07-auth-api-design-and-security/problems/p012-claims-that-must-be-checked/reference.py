class InvalidClaim(Exception):
    """A claim of a signed token is missing or wrong. `reason` names which one."""

    def __init__(self, reason: str):
        super().__init__(reason)
        self.reason = reason


def _is_number(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def check_claims(claims: dict, now: float, issuer: str, audience: str, leeway: float = 30) -> dict:
    sub = claims.get("sub")
    if not isinstance(sub, str) or not sub:
        raise InvalidClaim("missing_sub")

    exp = claims.get("exp")
    if not _is_number(exp):
        raise InvalidClaim("missing_exp")
    if now - leeway >= exp:
        raise InvalidClaim("expired")

    if "nbf" in claims:
        nbf = claims["nbf"]
        if not _is_number(nbf):
            raise InvalidClaim("bad_nbf")
        if nbf > now + leeway:
            raise InvalidClaim("not_yet_valid")

    if claims.get("iss") != issuer:
        raise InvalidClaim("wrong_issuer")

    aud = claims.get("aud")
    if isinstance(aud, str):
        allowed = aud == audience
    elif isinstance(aud, list):
        allowed = audience in aud
    else:
        allowed = False
    if not allowed:
        raise InvalidClaim("wrong_audience")
    return claims
