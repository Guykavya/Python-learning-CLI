class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False


def longest_common_prefix(words):
    if not words:
        return ""
    root = TrieNode()
    for w in words:
        node = root
        for ch in w:
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]
        node.is_end = True
    node, prefix = root, []
    while len(node.children) == 1 and not node.is_end:
        ch = next(iter(node.children))          # the only key
        prefix.append(ch)
        node = node.children[ch]
    return "".join(prefix)
