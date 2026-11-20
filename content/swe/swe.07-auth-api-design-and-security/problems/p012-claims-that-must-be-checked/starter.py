class InvalidClaim(Exception):
    """A claim of a signed token is missing or wrong. `reason` names which one."""

    def __init__(self, reason: str):
        super().__init__(reason)
        self.reason = reason


def check_claims(claims: dict, now: float, issuer: str, audience: str, leeway: float = 30) -> dict:
    # TODO: the six rules of problem.md, in order; raise InvalidClaim(reason) at the first failure
    return claims
