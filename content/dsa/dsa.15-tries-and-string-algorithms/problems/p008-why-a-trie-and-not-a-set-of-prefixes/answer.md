## Model answer

**1. "O(1)" lookups.** A set lookup is `O(1)` only in the number of stored items. Before looking up `prefix`, Python must **hash** the string, which reads all its `p` characters (the first time; strings cache their hash), and on a hit it compares the strings character by character. So `starts_with` costs `O(p)`, the same as walking `p` levels of a trie. The set does not win on query time; it only looks simpler.

**2. Insert cost.** `word[:k]` builds a **new string** of length `k` for every `k` from 0 to `L`. Together that is `0 + 1 + ... + L = L(L + 1)/2` characters copied and hashed: `O(L**2)` per word. The trie's insert walks `L` letters and creates at most `L` nodes: `O(L)`.

**3. Memory.** The prefixes of one word hold `L(L + 1)/2` characters: for `L = 10`, `55` characters in 11 strings, against 10 characters in the word. For 10**5 words of length 10 with no shared prefixes, that is about 5.5 million characters in 1.1 million string objects, and every string object carries its own overhead of several dozen bytes. The trie needs at most one node per letter, 10**6 nodes, and fewer when words share beginnings (shared prefixes are stored once in both, but the set still pays `O(L**2)` for every word with a unique tail).

**4. What the sets cannot do cheaply.**
- **Autocomplete / listing words below a prefix**: the trie walks to the prefix node and does a DFS of that subtree. The sets know only *that* the prefix exists, not which words continue it; you would have to scan all words.
- **Shortest root (p007), longest common prefix, wildcard search with `.`, counts per prefix, Word Search II pruning**: all follow the **path structure**, which a set does not have.
- **Deletion**: removing a word means removing those of its prefixes that no other word uses, which needs counts per prefix (a dict of counts), again `O(L**2)` per word.

**5. When the classmate is right.** For a **small** dictionary with **short** words and only yes/no questions (`search` and `starts_with`), the sets are short, correct and fast in practice, because hashing is done in C. For a static list that needs prefix **ranges**, a **sorted list with `bisect`** is even better: all words with a prefix form one contiguous block, no nodes at all. A trie earns its memory when words are long, change often, or the questions follow the paths (listing, counting, wildcards, shortest roots).

**Checklist: your answer should mention**
- [ ] hashing a string reads all of it: a lookup is `O(p)`, not `O(1)`, in the length of the prefix
- [ ] `insert` builds `L + 1` slices: `O(L**2)` characters, against `O(L)` for the trie
- [ ] the memory count `L(L + 1)/2` (55 for `L = 10`), and string-object overhead per prefix
- [ ] the trie stores each **shared** prefix once, as one node per letter
- [ ] at least two operations that need the **path structure**: listing / autocomplete, counts, deletion, shortest root, wildcards
- [ ] a fair case for the sets or a **sorted list + bisect** (small, static, short words, yes/no questions)
