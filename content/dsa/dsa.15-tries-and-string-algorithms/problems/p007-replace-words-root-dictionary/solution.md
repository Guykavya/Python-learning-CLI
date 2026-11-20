## Approach

Chapter section 7. Put the roots in a trie. Walk each word down the trie and **stop at the first node that ends a root**: the walk goes one letter at a time, so the first root found is the shortest.

```python
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
```

## Complexity

Building: `O(total letters of the roots)`. Each word: `O(min(len(word), longest root))`, because the walk stops when the trie path ends. Total `O(roots + sentence)`.

## Another way

A set of roots and `for k in range(1, len(word) + 1): if word[:k] in roots: ...`. It is correct and short, but each `word[:k]` is a new string of length `k` that must be built and hashed: `O(L**2)` per word in the worst case. With a limit on root length (`k <= longest root`) it is fine in practice. The starter's "try every root in list order" is both slow (`O(number of roots)` per word) and wrong, because the first matching root in the list need not be the shortest.
