class ArrayNode:
    def __init__(self):
        self.next = [None] * 26    # slot i is the child for chr(97 + i)
        self.is_end = False


class ArrayTrie:
    def __init__(self):
        self.root = ArrayNode()
        self.node_count = 1

    def insert(self, word):
        """Store word (lowercase letters only)."""

    def search(self, word):
        return False

    def starts_with(self, prefix):
        return False
