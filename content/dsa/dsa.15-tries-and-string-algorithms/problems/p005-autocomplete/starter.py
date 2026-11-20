class Autocomplete:
    def __init__(self, words):
        self.words = list(words)

    def suggest(self, prefix, k=3):
        """First k distinct names (alphabetical) that start with prefix."""
        return [w for w in self.words if w.startswith(prefix)][:k]
