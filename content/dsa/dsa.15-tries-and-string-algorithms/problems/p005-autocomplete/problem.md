# Autocomplete

A search box shows up to `k` suggestions while the user types. Write a class `Autocomplete` (chapter section 6):

- `Autocomplete(words)`: build it once from a list of product names (duplicates may appear; each name is suggested once);
- `suggest(prefix, k=3)`: the first `k` names, in **alphabetical order**, that start with `prefix`.

`suggest("")` gives the first `k` names of the whole list in alphabetical order.

## Example

```python
>>> ac = Autocomplete(["mobile", "mouse", "moneypot", "monitor", "mousepad"])
>>> ac.suggest("m")
['mobile', 'moneypot', 'monitor']
>>> ac.suggest("mou")
['mouse', 'mousepad']
>>> ac.suggest("mouse", k=1)
['mouse']
>>> ac.suggest("x")
[]
>>> Autocomplete(["bat", "bar", "bark", "ball"]).suggest("")
['ball', 'bar', 'bark']
```

## Constraints

- Up to 5 * 10**4 names of lowercase letters; up to 2 * 10**4 calls to `suggest`; `0 <= k <= 10`.
- A call must not look at all the names, and must not collect **every** name below the prefix when only `k` are needed: a short prefix like `"a"` can have thousands of matches.

## Think about

1. In a trie, in which order must you visit the children so that the names come out alphabetically?
2. A name that ends at a node comes **before** the longer names below it (`mouse` before `mousepad`). Where in your DFS do you record it?
3. How do you stop the search as soon as `k` names are found?
