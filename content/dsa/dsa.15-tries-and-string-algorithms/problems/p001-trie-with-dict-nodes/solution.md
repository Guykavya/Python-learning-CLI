## Approach

Chapter section 3. A node stands for the string on the path from the root; `children` maps the next letter to the next node; `is_end` marks the nodes where an inserted word stops.

- `insert` walks the word, **creating** missing children, and sets `is_end` on the last node.
- `_walk` follows a string and gives up (`None`) at the first missing edge.
- `search` = `_walk` + "a word ends here". `starts_with` = `_walk` + "some word goes on from here": the node has a child or ends a word. Every node made by `insert` passes that test except the root of an **empty** trie, so the check only matters for `starts_with("")` before anything is inserted.

```python
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
```

The empty word walks zero letters, so `insert("")` marks the **root** as a word end, and `starts_with("")` is `True` as soon as any word is stored.

## Complexity

Each operation does one dict lookup per letter: `O(L)` for a word of length `L`, independent of the number of words stored. Memory is one node per distinct prefix: at most the total number of letters inserted, less when words share beginnings.

## Another way

`children.setdefault(ch, TrieNode())` shortens `insert` to two lines, but it builds a new (unused) `TrieNode` for every letter, even when the child already exists: correct, but wasteful. For a fixed small alphabet, a 26-slot list per node also works (p002).
