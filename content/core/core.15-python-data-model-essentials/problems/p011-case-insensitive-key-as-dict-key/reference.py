class HeaderName:
    def __init__(self, text):
        self.text = text
        self._key = text.casefold()

    def __eq__(self, other):
        if not isinstance(other, HeaderName):
            return NotImplemented
        return self._key == other._key

    def __hash__(self):
        return hash(self._key)

    def __repr__(self):
        return f"HeaderName({self.text!r})"

    def __str__(self):
        return self.text
