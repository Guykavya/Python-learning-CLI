## Hint 1

Build a trie once. For a query, walk to the prefix node (`O(len(prefix))`); if the path breaks, the answer is `[]`. Then do a depth-first search below that node, visiting children in **sorted** order of their letters, and record a name whenever a node is a word end, **before** going into its children.

## Hint 2

Pass the target `k` into the DFS and return as soon as the output list holds `k` names. Then a query costs about the length of the names it returns plus the nodes on the way, not the size of the subtree.

## Hint 3

```
def dfs(node, path, out, k):
    if len(out) == k: return
    if node.is_end: out.append("".join(path))
    for ch in sorted(node.children):
        if len(out) == k: return
        path.append(ch); dfs(node.children[ch], path, out, k); path.pop()
```

Sorting the children at every visit costs a little; you may also store each node's children already sorted once the trie is built.
