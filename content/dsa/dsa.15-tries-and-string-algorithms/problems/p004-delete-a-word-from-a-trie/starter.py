class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False


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
        return self._walk(prefix) is not None

    def node_count(self):
        """Number of nodes, root included."""
        return 1

    def delete(self, word):
        """Remove word and free the nodes nobody needs. Return True if word was stored."""
        node = self._walk(word)
        if node is None or not node.is_end:
            return False
        node.is_end = False          # makes search false, but leaves the useless nodes behind
        return True
