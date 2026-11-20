class ArrayNode:
    def __init__(self):
        self.next = [None] * 26    # slot i is the child for chr(97 + i)
        self.is_end = False


class ArrayTrie:
    def __init__(self):
        self.root = ArrayNode()
        self.node_count = 1

    def insert(self, word):
        node = self.root
        for ch in word:
            i = ord(ch) - 97
            if node.next[i] is None:
                node.next[i] = ArrayNode()
                self.node_count += 1
            node = node.next[i]
        node.is_end = True

    def _walk(self, text):
        node = self.root
        for ch in text:
            node = node.next[ord(ch) - 97]
            if node is None:
                return None
        return node

    def search(self, word):
        node = self._walk(word)
        return node is not None and node.is_end

    def starts_with(self, prefix):
        node = self._walk(prefix)
        return node is not None and (node.is_end or any(c is not None for c in node.next))
