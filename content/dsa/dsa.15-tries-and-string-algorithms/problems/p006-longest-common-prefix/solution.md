## Approach

Chapter section 7. In a trie of the words, the common prefix is the path from the root **while there is no choice**. Two things end it:

- **a branch**: the node has two or more children, so the words disagree on the next letter;
- **a word end**: some word stops here, so it has no next letter to share (`["abc", "ab"]` gives `"ab"`).

```python
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
```

If one word is `""`, the root itself is a word end, and the loop never starts: the answer is `""`.

## Complexity

Building the trie is `O(total letters)` time and memory; the walk is `O(answer length)`.

## Another way

For a single question, a trie is overkill. Two cheaper ways from the chapter:

- **Vertical scan:** compare column `i` of every word with `words[0][i]`; stop at the first mismatch or the end of the shortest word. `O(total letters)`, no extra memory.
- **Min and max:** `lo, hi = min(words), max(words)`; the common prefix of all words is the common prefix of these two (alphabetically, the most different pair). `os.path.commonprefix(words)` does this for you.

The trie wins only when the same list is asked many prefix questions.
