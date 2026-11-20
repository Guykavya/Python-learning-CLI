# Trie with array nodes

Write `ArrayTrie` (chapter section 4), the same trie as p001 but with a **list of 26 slots** per node instead of a dict. Slot `0` is the child for `a`, slot `25` the child for `z`, and `None` means "no child".

- `ArrayTrie()`: `self.root` is an `ArrayNode`; `self.node_count` is the number of nodes, counting the root (so it starts at 1).
- `insert(word)`, `search(word)`, `starts_with(prefix)`: as in p001.

Each `ArrayNode` has `next`, a list of 26 entries, and `is_end`. `starter.py` gives you `ArrayNode`. Words use only the lowercase letters `a` to `z` (and may be empty).

## Example

```python
>>> t = ArrayTrie()
>>> for w in ["car", "card", "care", "cat", "dog", "dot"]:
...     t.insert(w)
>>> t.node_count, t.search("care"), t.search("ca"), t.starts_with("do")
(11, True, False, True)
>>> len(t.root.next), t.root.next[2] is None, t.root.next[0] is None
(26, False, True)
```

The six words have 20 letters, but only 11 nodes, because beginnings are shared.

## Constraints

- Lowercase letters only. Every operation costs `O(len(word))`.
- As in p001, `starts_with("")` is `False` for an empty trie and `True` once any word is stored.
- `node_count` must be exact: it counts nodes, not letters, and inserting a word twice adds nothing.

## Think about

1. How do you turn a letter into its slot number, and back?
2. When must `node_count` grow, and by how much?
3. In this example, how many slots are reserved in total, and how many are used? (Chapter section 4, "Dict nodes versus array nodes".)
