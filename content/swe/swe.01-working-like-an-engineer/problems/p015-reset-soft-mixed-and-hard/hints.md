## Hint 1

All three modes move the branch to `HEAD~1` (commit 2, subject `c-b`). They differ in what they do with the **index** and the **working tree**. Which modes touch which place? (Table in chapter section 9.2.)

## Hint 2

Starting point: tip `c-c`; index = commit 3 plus the staged `a.txt` edit; working tree = the index plus the unstaged `b.txt` edit. After the branch moves to commit 2, compare the index with the **new** tip to see what is "staged".

## Hint 3

`soft`: index and working tree stay as they were, so `c.txt` (new compared to commit 2) and the `a.txt` edit show as staged, the `b.txt` edit as unstaged. `mixed`: the index is reset to commit 2, so nothing is staged; both edits are unstaged and `c.txt` is untracked. `hard`: index and working tree both become commit 2: edits gone, `c.txt` removed from disk.
