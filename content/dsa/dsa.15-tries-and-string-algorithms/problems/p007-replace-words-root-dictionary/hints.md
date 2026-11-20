## Hint 1

Put the roots in a trie. For each word, walk its letters from the root of the trie. The **first** node you reach that ends a root gives the shortest root: return `word[:i + 1]` right away.

## Hint 2

Two ways to fail: the next letter has no child (no root is a prefix), or the word runs out first (it is shorter than every root on its path). In both cases keep the word.

## Hint 3

```
shortest_root(word):
    node = trie root
    for i, ch in enumerate(word):
        if ch not in node.children: return word
        node = node.children[ch]
        if node.is_end: return word[:i + 1]
    return word
answer = " ".join(shortest_root(w) for w in sentence.split())
```
