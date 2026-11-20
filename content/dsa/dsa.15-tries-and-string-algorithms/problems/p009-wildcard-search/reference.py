class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False


class WordDictionary:
    def __init__(self):
        self.root = TrieNode()

    def add_word(self, word):
        node = self.root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]
        node.is_end = True

    def search(self, pattern):
        def match(node, i):
            if i == len(pattern):
                return node.is_end                      # the word must end exactly here
            ch = pattern[i]
            if ch == ".":
                return any(match(child, i + 1) for child in node.children.values())
            child = node.children.get(ch)
            return child is not None and match(child, i + 1)

        return match(self.root, 0)
