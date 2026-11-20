class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False


class Autocomplete:
    def __init__(self, words):
        self.root = TrieNode()
        for w in words:
            node = self.root
            for ch in w:
                if ch not in node.children:
                    node.children[ch] = TrieNode()
                node = node.children[ch]
            node.is_end = True

    def suggest(self, prefix, k=3):
        node = self.root
        for ch in prefix:
            if ch not in node.children:
                return []
            node = node.children[ch]
        out = []
        path = list(prefix)

        def dfs(node):
            if node.is_end:
                out.append("".join(path))         # a shorter name comes before the names below it
            for ch in sorted(node.children):      # alphabetical order
                if len(out) >= k:
                    return
                path.append(ch)
                dfs(node.children[ch])
                path.pop()

        if k > 0:
            dfs(node)
        return out[:k]
