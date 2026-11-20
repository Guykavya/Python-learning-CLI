## Approach

Chapter section 5. Two counters per node:

- `pass_count`: how many logged words go through the node, so `count_prefix` reads it at the prefix's node;
- `end_count`: how many end exactly there, so `count_equal` reads it at the word's node.

The chapter's `CountTrie` does not count the root, so its `count_words_with_prefix("")` would be 0. Here the root is counted too, so `count_prefix("")` is the total number of logged words.

```python
class CountNode:
    def __init__(self):
        self.children = {}
        self.pass_count = 0     # words that go through this node
        self.end_count = 0      # words that end exactly here


class CountTrie:
    def __init__(self):
        self.root = CountNode()

    def insert(self, word):
        node = self.root
        node.pass_count += 1                    # every word passes the root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = CountNode()
            node = node.children[ch]
            node.pass_count += 1
        node.end_count += 1

    def _find(self, text):
        node = self.root
        for ch in text:
            if ch not in node.children:
                return None
            node = node.children[ch]
        return node

    def count_equal(self, word):
        node = self._find(word)
        return node.end_count if node else 0

    def count_prefix(self, prefix):
        node = self._find(prefix)
        return node.pass_count if node else 0
```

Check the example: through `car` go `car`, `car`, `card`, `care` (4); through `ca` also `cat` (5).

## Complexity

`O(L)` for every operation; the counts are kept up to date during `insert`, so a query never looks below the prefix node.

## Another way

Without counters: walk to the prefix node and count the word ends in its whole subtree with a DFS. That is correct, but each query costs the size of the subtree: `count_prefix("")` would visit the whole trie, every time.
