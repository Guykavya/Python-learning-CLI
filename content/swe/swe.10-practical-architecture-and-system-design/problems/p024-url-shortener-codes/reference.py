import re

ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
ALIAS = re.compile(r"[A-Za-z0-9_-]{3,32}")


class InvalidAlias(ValueError):
    pass


class AliasTaken(ValueError):
    pass


def encode(n):
    if n < 0:
        raise ValueError("only non-negative numbers can be encoded")
    if n == 0:
        return ALPHABET[0]
    digits = []
    while n:
        n, remainder = divmod(n, 62)
        digits.append(ALPHABET[remainder])
    return "".join(reversed(digits))


def decode(code):
    if not code:
        raise ValueError("an empty code")
    n = 0
    for ch in code:
        if ch not in ALPHABET:
            raise ValueError(f"{ch!r} is not a base62 character")
        n = n * 62 + ALPHABET.index(ch)
    return n


class Shortener:
    def __init__(self, reserved=("api", "admin", "login", "static", "health")):
        self.reserved = {word.lower() for word in reserved}
        self.urls = {}
        self.codes = {}
        self.counter = 1

    def _store(self, code, url):
        self.urls[code.lower()] = url
        self.codes[code.lower()] = code
        return code

    def create(self, url, alias=None):
        if alias is not None:
            if not ALIAS.fullmatch(alias):
                raise InvalidAlias("an alias has 3 to 32 characters: letters, digits, '-' and '_'")
            if alias.lower() in self.reserved:
                raise InvalidAlias(f"{alias!r} is a reserved word")
            if alias.lower() in self.urls:
                raise AliasTaken(f"{alias!r} is already taken")
            return self._store(alias, url)
        while True:
            code = encode(self.counter).rjust(7, "0")
            self.counter += 1                                    # a skipped value is never used again
            if code.lower() not in self.urls:
                return self._store(code, url)

    def resolve(self, code):
        return self.urls.get(code.lower())
