## Approach

Chapter section 6: walk to the prefix node, then a depth-first search below it.

- **Alphabetical order** comes from visiting the children in sorted order, and recording a node's own name **before** its children (`mouse` < `mousepad`, because a prefix sorts before every longer string that starts with it).
- **Stopping early**: as soon as `k` names are found, return. Without that, `suggest("a")` would list thousands of names only to keep three.
- **Duplicates** disappear by themselves: a name is a single node with `is_end = True`, however often it was inserted.

```python
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
```

## Complexity

Walking to the prefix: `O(p)`. The DFS stops after `k` names, so it visits roughly the nodes on the paths to those names plus the dead ends next to them: about `O(k * L * alphabet)` in the worst case, independent of how many names match. The recursion depth is the length of the longest name.

## Another way

No trie at all: sort the distinct names once, then for each query use `bisect_left(names, prefix)` (dsa.06) and take up to `k` names from there while they still start with the prefix. Names that start with a prefix form one **contiguous block** of a sorted list, so this is `O(log n + k * L)` per query and very short to write. The trie wins when names are added and removed all the time, or when each node stores extra data (frequencies, top-k).
