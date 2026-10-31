class Sentence:
    def __init__(self, words):
        self._words = list(words)

    def __repr__(self):
        return f"Sentence({self._words!r})"

    def __len__(self):
        return len(self._words)

    def __getitem__(self, key):
        if isinstance(key, slice):
            return type(self)(self._words[key])
        if isinstance(key, int):
            return self._words[key]
        raise TypeError("indices must be integers or slices")

    def __str__(self):
        return " ".join(self._words)
