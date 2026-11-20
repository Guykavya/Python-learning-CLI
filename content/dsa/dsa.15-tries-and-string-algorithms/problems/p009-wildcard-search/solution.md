## Approach

Chapter section 7. Store the words in a trie. Search with a recursive walk:

- a letter follows its one edge, or fails if it is missing;
- a `.` tries **every** child and succeeds as soon as one succeeds (backtracking, dsa.07);
- at the end of the pattern the node must be a word end, so lengths must agree.

```python
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
```

## Complexity

Without dots: `O(L)`. With dots, the search can branch, but it visits each trie node at most once per pattern (every node has one depth, and the pattern position equals the depth), so the worst case is `O(number of trie nodes)`. Failing patterns full of dots are the expensive ones (chapter section 7, "Try it"): they must try every branch.

## Another way

Group the words by length: `by_len[L]` is a list (or a trie) of the words of length `L`. A pattern is then only compared with words of its own length. For few dots, another trick is to store every word with each position replaced by `.` in a set (`"b.d"`, `".ad"`, ...): a one-dot pattern is then a single set lookup. That costs `L` extra entries per word and only works for a fixed number of dots.
