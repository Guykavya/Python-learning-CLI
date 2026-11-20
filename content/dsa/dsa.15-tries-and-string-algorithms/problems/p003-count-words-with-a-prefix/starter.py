class CountNode:
    def __init__(self):
        self.children = {}
        self.pass_count = 0     # words that go through this node
        self.end_count = 0      # words that end exactly here


class CountTrie:
    def __init__(self):
        self.root = CountNode()

    def insert(self, word):
        """Log one more copy of word."""

    def count_equal(self, word):
        return 0

    def count_prefix(self, prefix):
        return 0
