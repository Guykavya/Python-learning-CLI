## Approach

Chapter section 8: one depth-first search from every cell, walking the **trie** at the same time.

- The trie is a dict of dicts; the key `"$"` (not a letter) holds the word that ends at a node.
- A neighbour is visited only if its letter is a child of the current trie node: this prunes every direction in which no word continues.
- `board[r][c] = "#"` marks the cell as used on the current path; the letter is restored on the way back, so other paths and other words can use it.
- `node.pop("$")` records a word once.
- `if not node: del parent[ch]` removes branches that hold nothing any more, so finished parts of the trie are never explored again.

```python
def find_words(board, words):
    root = {}                                  # dict-of-dicts trie; "$" holds a finished word
    for w in words:
        node = root
        for ch in w:
            node = node.setdefault(ch, {})
        node["$"] = w

    rows, cols = len(board), len(board[0])
    found = []

    def dfs(r, c, parent):
        ch = board[r][c]
        node = parent[ch]
        if "$" in node:
            found.append(node.pop("$"))        # take the word: never report it twice
        board[r][c] = "#"                      # mark the cell as used
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and board[nr][nc] in node:
                dfs(nr, nc, node)
        board[r][c] = ch                       # restore (backtrack)
        if not node:                           # nothing left below: cut this branch away
            del parent[ch]

    for r in range(rows):
        for c in range(cols):
            if board[r][c] in root:
                dfs(r, c, root)
    return sorted(found)
```

On the big test board (12 by 12, almost all `a`) the trie search took 0.29 s and one search per word took 39 s, both measured in an earlier test run on the author's machine. The words that cannot be traced are what cost the per-word search so much: each one must try every path before giving up, and the same `aaaa...` paths are tried again for every word.

## Complexity

Each start cell explores at most `3**(L - 1)` paths of length `L` after the first step (never straight back), so the worst case is `O(R * C * 3**L)`, **independent of the number of words**: the trie shares their prefixes. Building the trie is `O(total letters)`. The recursion depth is at most `L`.

## Another way

Without the branch deletion the search is still correct, but on boards like the test's it keeps exploring `a`-paths below branches whose words were already found. A different speed-up is to drop every word that uses a letter more often than the board has it, before searching. That helps, but it does not replace the trie: the test's words pass that check and still cannot be traced.
