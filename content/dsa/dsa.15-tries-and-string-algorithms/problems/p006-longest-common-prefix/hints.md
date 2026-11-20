## Hint 1

The common prefix is the path from the root as long as every word agrees on the next letter. In the trie that means: the current node has **exactly one child**, and **no word ends** at it (a word that ends has no next letter to share).

## Hint 2

```
build the trie
node, prefix = root, []
while len(node.children) == 1 and not node.is_end:
    ch = the only key of node.children
    prefix.append(ch); node = node.children[ch]
return "".join(prefix)
```

## Hint 3

Without a trie: compare column by column. For `i = 0, 1, 2, ...`, take `words[0][i]` and check that every other word is long enough and has the same letter there; return `words[0][:i]` at the first difference.
