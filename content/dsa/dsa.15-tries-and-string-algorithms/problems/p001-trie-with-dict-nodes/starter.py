class TrieNode:
    def __init__(self):
        self.children = {}     # letter -> TrieNode
        self.is_end = False    # does a word end exactly here?


class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        """Store word."""

    def search(self, word):
        """True if exactly this word was inserted."""
        return False

    def starts_with(self, prefix):
        """True if some inserted word starts with prefix."""
        return False
