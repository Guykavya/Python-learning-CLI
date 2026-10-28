class Sentence:
    def __init__(self, words):
        self._words = list(words)

    def __repr__(self):
        return f"Sentence({self._words!r})"

    # TODO: __len__, __getitem__ (int -> word, slice -> Sentence), __str__
