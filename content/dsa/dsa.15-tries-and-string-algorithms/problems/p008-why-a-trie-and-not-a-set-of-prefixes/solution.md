## Approach

Measure both structures in the same units: characters read, characters stored, and which questions each one can answer.

| | `PrefixSets` | Trie |
|---|---|---|
| `starts_with(p)` | hash `p`: `O(p)` | walk `p` nodes: `O(p)` |
| `insert(word)` | `L + 1` slices: `O(L**2)` | `O(L)` |
| memory per unshared word | `L(L + 1)/2` characters in `L + 1` strings | at most `L` nodes |
| list words with a prefix | scan everything | DFS below one node |
| shortest root, wildcards, counts | no structure to follow | follow the path |

## Model answer

See `answer.md`.

## What to check

- You did not accept "set lookups are `O(1)`" without asking about the **length** of the key.
- You computed a number (55 characters for `L = 10`), not just "more memory".
- You named operations that need **paths**, not only yes/no questions.
- You gave the sets a fair case: small, static data, or a sorted list with `bisect`.

## Another way

Measure instead of arguing: build both structures for 10**4 random words and compare `sys.getsizeof` of every stored string (or `tracemalloc`) and the time of the inserts. Treat any numbers as machine-specific, and check that the trend matches the `L**2` against `L` argument when you double `L`.
