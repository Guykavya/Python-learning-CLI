ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"


class InvalidAlias(ValueError):
    pass


class AliasTaken(ValueError):
    pass


def encode(n):
    # TODO: base62, most significant digit first
    return ""


def decode(code):
    # TODO
    return 0


class Shortener:
    def __init__(self, reserved=("api", "admin", "login", "static", "health")):
        self.reserved = {word.lower() for word in reserved}
        self.urls = {}                    # lower-cased code -> url
        self.codes = {}                   # lower-cased code -> the code as stored
        self.counter = 1

    def create(self, url, alias=None):
        # TODO
        return ""

    def resolve(self, code):
        # TODO
        return None
