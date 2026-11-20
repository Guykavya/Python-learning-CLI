# Delete a word from a trie

A spell checker lets users remove words from their personal dictionary. Extend the dict trie of p001 with:

- `delete(word)`: remove `word`; return `True` if it was stored, `False` otherwise (then nothing changes);
- `node_count()`: the number of nodes, counting the root.

Deleting must **free the nodes nobody needs any more**: after any sequence of inserts and deletes, the trie must have exactly one node per distinct prefix of the words still stored (plus the root). Other words must be untouched. (Chapter section 5, "Deleting from a plain trie".)

## Example

```python
>>> t = Trie()
>>> for w in ["car", "card", "cat"]:
...     t.insert(w)
>>> t.node_count()
6
>>> t.delete("card"), t.node_count(), t.search("car")
(True, 5, True)
>>> t.delete("cat"), t.node_count(), t.starts_with("ca")
(True, 4, True)
>>> t.delete("ca"), t.delete("dog")        # a prefix only, and a word never stored
(False, False)
>>> t.delete("car"), t.node_count()
(True, 1)
```

## Constraints

- Any characters; the empty word may be inserted and deleted (it lives on the root, which is never removed).
- `delete` costs `O(len(word))`.

## Think about

1. When may a node be removed? Name both conditions.
2. Why must the pruning go from the **bottom up**, and when must it stop?
3. Inserting a word twice and deleting it once: is it still stored? (Here: no. A plain trie stores a set of words, not counts.)
