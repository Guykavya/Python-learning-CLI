## Hint 1

Every node stands for the string read along the path from the root. To insert, walk the letters from the root: if the child for the letter is missing, create a new `TrieNode` and store it in `children`; then step into it. After the last letter, set `is_end = True`.

## Hint 2

`search` and `starts_with` both need the same walk: follow the letters and stop with "not found" the moment a child is missing. Write that walk once, as a helper that returns the node or `None`.

## Hint 3

```
_walk(text):
    node = root
    for ch in text:
        if ch not in node.children: return None
        node = node.children[ch]
    return node

search(word)       = node is not None and node.is_end    (node = _walk(word))
starts_with(prefix) = node is not None and (node.children or node.is_end)
                      (only the root of an empty trie fails the second part)
```
