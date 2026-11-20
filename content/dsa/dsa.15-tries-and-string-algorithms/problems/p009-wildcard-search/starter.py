class WordDictionary:
    def __init__(self):
        self.words = []

    def add_word(self, word):
        self.words.append(word)

    def search(self, pattern):
        """True if a stored word matches pattern ('.' = exactly one letter)."""
        return any(all(p == "." or p == c for p, c in zip(pattern, w)) for w in self.words)
