## Hint 1

Keep three boxes in your head: **committed** (what the last commit holds), **index** (what `git add` copied), **working tree** (the file on disk). `git diff` compares working tree with index. `git diff --staged` compares index with the last commit.

## Hint 2

Start: all three boxes hold `v1`. After `echo v2 > app.py` only the working tree box changed, so the working tree differs from the index (diff = yes) and the index equals the commit (staged = no).

## Hint 3

Track the boxes (commit / index / working tree): start `v1 v1 v1`; after 1: `v1 v1 v2`; after 2: `v1 v2 v2`; after 3: `v1 v2 v3`; after 4 the index goes back to the commit's version; after 5 the index copies the working tree; after 6 the commit copies the index; after 7 only the working tree changes.
