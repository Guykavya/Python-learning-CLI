# Trie with dict nodes

Write a class `Trie` (chapter section 3) with:

- `Trie()`: an empty trie. Its root is `self.root`, a `TrieNode`.
- `insert(word)`: store the word.
- `search(word)`: `True` if exactly this word was inserted.
- `starts_with(prefix)`: `True` if some inserted word starts with `prefix`.

Each node is a `TrieNode` with two fields: `children`, a `dict` from a letter to the child node, and `is_end`, a `bool` that says whether a word ends exactly at this node. `starter.py` gives you `TrieNode`; the tests look at `root.children` to check that you really built a tree of letters.

## Example

```python
>>> t = Trie()
>>> for w in ["car", "card", "cat"]:
...     t.insert(w)
>>> t.search("car"), t.search("ca"), t.search("cards")
(True, False, False)
>>> t.starts_with("ca"), t.starts_with("cb"), t.starts_with("")
(True, False, True)
>>> sorted(t.root.children)
['c']
```

## Constraints

- Words may contain any characters (letters, digits, capitals, spaces). The empty word `""` may be inserted: then `search("")` is `True`. `starts_with("")` is `True` once any word is stored, and `False` for an empty trie.
- Every operation must cost `O(len(word))`, whatever the number of stored words. The tests insert 10**5 words and ask 2 * 10**5 questions.

## Think about

1. `search("ca")` and `starts_with("ca")` walk the same path. What is the one extra thing `search` checks, and why?
2. Where does the empty word live in the tree?
3. What should happen when the same word is inserted twice?
