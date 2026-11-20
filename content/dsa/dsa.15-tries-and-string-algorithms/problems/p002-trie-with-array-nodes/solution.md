## Approach

Chapter section 4. The only change from the dict trie (p001) is how a child is found: `node.next[ord(ch) - 97]`, a list index, with `None` for "no child". `node_count` grows by one exactly when a node is created.

```python
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
```

**Memory.** The example has 11 nodes, so `11 * 26 = 286` slots are reserved, but only 10 are used (one per edge). The dict version stores just those 10 entries. Arrays pay off when the alphabet is tiny (2 for bits, 10 for digits), not for 26 letters with few children per node.

## Complexity

`O(L)` per operation. Memory: `26` slots per node, always.

## Another way

The flat-table version of chapter section 4: no node objects at all, one list of rows `nxt[v]` with 26 child **numbers** (`-1` = none) and a list `end[v]`. `node_count` is then simply `len(nxt)`.
