from urllib.parse import urlsplit


class CookieJar:
    def __init__(self):
        self._cookies = {}

    def store(self, url, set_cookie, now):
        # TODO: parse "name=value; Attr; Attr=value"
        pass

    def header_for(self, url, now):
        return ""

    def all(self, now):
        return []
