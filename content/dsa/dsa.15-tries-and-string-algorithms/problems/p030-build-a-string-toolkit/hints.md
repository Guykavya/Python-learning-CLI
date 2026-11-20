## Hint 1

Reuse what you wrote: the dict trie of p001 with the counters of p003, the autocomplete DFS of p005 (all words, sorted), `prefix_function` of p014, `kmp_search` of p015 and `z_function` of p021. Put shared logic in helpers (`_walk`).

## Hint 2

Keep `pass_count` on every node, the root included (every word passes the root). Then `count_prefix(p)` is the walked node's `pass_count` (0 if the walk breaks), and `starts_with(p)` can simply be `count_prefix(p) > 0`: that also answers `starts_with("")` correctly for an empty trie.

## Hint 3

For `words_with_prefix`, walk to the prefix node, then a DFS that visits children in sorted order and records a word **before** its children. Use an explicit stack (or raise the recursion limit) if words can be very long.
