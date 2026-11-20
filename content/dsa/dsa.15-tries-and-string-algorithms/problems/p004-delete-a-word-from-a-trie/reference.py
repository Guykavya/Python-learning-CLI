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
        count, stack = 0, [self.root]
        while stack:                       # iterative: no recursion limit on long words
            node = stack.pop()
            count += 1
            stack.extend(node.children.values())
        return count

    def delete(self, word):
        node = self.root
        path = []                          # (parent, letter) pairs, top to bottom
        for ch in word:
            if ch not in node.children:
                return False               # never inserted
            path.append((node, ch))
            node = node.children[ch]
        if not node.is_end:
            return False                   # only a prefix of something
        node.is_end = False
        for parent, ch in reversed(path):  # prune from the bottom up
            child = parent.children[ch]
            if child.children or child.is_end:
                break                      # still needed by another word
            del parent.children[ch]
        return True
