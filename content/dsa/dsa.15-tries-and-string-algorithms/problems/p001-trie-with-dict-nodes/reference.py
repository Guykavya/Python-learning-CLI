class TrieNode:
    def __init__(self):
        self.children = {}     # letter -> TrieNode
        self.is_end = False    # does a word end exactly here?


class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        node = self.root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]
        node.is_end = True

    def _walk(self, text):
        """Follow text from the root. Return the node, or None if the path breaks."""
        node = self.root
        for ch in text:
            if ch not in node.children:
                return None
            node = node.children[ch]
        return node

    def search(self, word):
        node = self._walk(word)
        return node is not None and node.is_end

    def starts_with(self, prefix):
        node = self._walk(prefix)
        return node is not None and (bool(node.children) or node.is_end)
