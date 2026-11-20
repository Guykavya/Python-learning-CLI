class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False


def replace_words(roots, sentence):
    root = TrieNode()
    for r in roots:
        node = root
        for ch in r:
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]
        node.is_end = True

    def shortest_root(word):
        node = root
        for i, ch in enumerate(word):
            if ch not in node.children:
                return word                  # no root is a prefix
            node = node.children[ch]
            if node.is_end:
                return word[:i + 1]          # first (= shortest) root found
        return word                          # word is shorter than any root on its path

    return " ".join(shortest_root(w) for w in sentence.split())
