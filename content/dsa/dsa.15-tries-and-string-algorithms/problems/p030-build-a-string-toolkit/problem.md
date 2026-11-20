# Build a string toolkit

Build one module, `solution.py`, that a later project can import as its string toolkit. It must contain:

| Name | What it does |
|---|---|
| `class Trie` | `insert(word)`, `search(word)`, `starts_with(prefix)`, `count_prefix(prefix)` (how many inserted words, with repeats, start with `prefix`), `words_with_prefix(prefix)` (the distinct stored words that start with `prefix`, sorted) |
| `prefix_function(s)` | the list `pi` (p014) |
| `kmp_search(text, pattern)` | all start positions, overlapping included; the empty pattern gives `0..len(text)` (p015) |
| `z_function(s)` | the list `z`, with `z[0] = len(s)` (p021) |

The tests are one **shared** test file: they check every part against Python's built-ins (`str.find` in a loop, `str.startswith`, list filtering, `os.path.commonprefix`) on thousands of random inputs, and they check that the parts agree with each other (for example, KMP and a Z-based search give the same positions). They also time each part on large inputs.

## Example

```python
>>> t = Trie()
>>> for w in ["car", "card", "care", "car", "dog"]:
...     t.insert(w)
>>> t.search("car"), t.search("ca"), t.starts_with("ca"), t.count_prefix("car")
(True, False, True, 4)
>>> t.words_with_prefix("car")
['car', 'card', 'care']
>>> prefix_function("abacaba"), z_function("abacaba")
([0, 0, 1, 0, 1, 2, 3], [7, 0, 1, 0, 3, 0, 1])
>>> kmp_search("aaaaa", "aa")
[0, 1, 2, 3]
```

## Constraints

- Any characters. The empty word, the empty pattern and the empty string must work.
- `Trie` operations are `O(len(word))` (and `words_with_prefix` also pays for the output); the three functions are linear.
- Words up to 10**5 per trie; strings up to 5 * 10**5 characters.

## Think about

1. Which parts can share code? (`kmp_search` needs `prefix_function`; the trie needs one walk helper.)
2. `starts_with("")` on an empty trie: what should it return, and does your `count_prefix` agree with it?
3. Which random inputs find the most bugs in string code? (Hint: a tiny alphabet such as `"ab"` makes many partial matches.)
