import hashlib
import hmac
import secrets


class ApiKeys:
    def __init__(self):
        self.rows = {}          # prefix -> record

    def create(self, owner: str) -> str:
        raise NotImplementedError("write create()")

    def check(self, presented: str):
        raise NotImplementedError("write check()")

    def revoke(self, prefix: str) -> None:
        raise NotImplementedError("write revoke()")
