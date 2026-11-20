## Approach

Chapter section 5. Two goals: make `search(word)` false, and free every node that no word needs any more.

A node is needed if it has a child (some longer word passes through it) or if it is the end of a word. Walk down remembering the path, clear `is_end`, then walk the path **backwards**, deleting childless non-end nodes, and **stop** at the first node that is still needed: everything above it is needed too.

```python
    def delete(self, word):
        node = self.root
        path = []                          # (parent, letter) pairs, top to bottom
        for ch in word:
            if ch not in node.children:
                return False               # never inserted
            path.append((node, ch))
            node = node.children[ch]
        if not node.is_end:
            return False                   # only a prefix of something
        node.is_end = False
        for parent, ch in reversed(path):  # prune from the bottom up
            child = parent.children[ch]
            if child.children or child.is_end:
                break                      # still needed by another word
            del parent.children[ch]
        return True

    def node_count(self):
        count, stack = 0, [self.root]
        while stack:                       # iterative: no recursion limit on long words
            node = stack.pop()
            count += 1
            stack.extend(node.children.values())
        return count
```

Trace of the example: deleting `card` removes `d` and stops at `r` (the end of `car`). Deleting `cat` removes `t` and stops at `a` (it still has the child `r`). Deleting `car` removes `r`, `a`, `c`: only the root is left.

## Complexity

`O(L)` time and `O(L)` extra space for the path. `node_count` visits every node: `O(size of the trie)`.

## Another way

Recursively (chapter section 5, "A recursive version"): `delete_rec(node, word, depth)` returns "my parent may delete me". It uses the call stack instead of the `path` list. Or with counters (p003): subtract along the path and drop a child whose `pass_count` reaches 0; that version also supports words inserted several times.
