class CountNode:
    def __init__(self):
        self.children = {}
        self.pass_count = 0     # words that go through this node
        self.end_count = 0      # words that end exactly here


class CountTrie:
    def __init__(self):
        self.root = CountNode()

    def insert(self, word):
        node = self.root
        node.pass_count += 1                    # every word passes the root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = CountNode()
            node = node.children[ch]
            node.pass_count += 1
        node.end_count += 1

    def _find(self, text):
        node = self.root
        for ch in text:
            if ch not in node.children:
                return None
            node = node.children[ch]
        return node

    def count_equal(self, word):
        node = self._find(word)
        return node.end_count if node else 0

    def count_prefix(self, prefix):
        node = self._find(prefix)
        return node.pass_count if node else 0
