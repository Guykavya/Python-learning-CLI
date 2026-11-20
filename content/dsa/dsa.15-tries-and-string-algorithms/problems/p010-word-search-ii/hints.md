## Hint 1

Put all the words in a trie. Start a DFS from every cell whose letter is a child of the trie root. In the DFS, move to a neighbour only if its letter is a **child of the current trie node**: if not, no word continues that way, and the whole direction is skipped. That pruning is the point of the trie.

## Hint 2

Mark the current cell as used (`board[r][c] = "#"`), explore the neighbours, then put the letter back. Store the whole word in the trie node where it ends (for example under a key `"$"`). When the DFS reaches such a node, record the word and **remove** it from the node so it is not reported again.

## Hint 3

```
def dfs(r, c, parent):
    ch = board[r][c]; node = parent[ch]
    if "$" in node: found.append(node.pop("$"))
    board[r][c] = "#"
    for each neighbour (nr, nc) inside the board:
        if board[nr][nc] in node: dfs(nr, nc, node)
    board[r][c] = ch
    if not node: del parent[ch]       # nothing left below: cut the branch
```

The last line is what keeps the all-`a` boards fast: once the words under a branch are found, the branch disappears.
