## Approach

| Mode | Branch | Index | Working tree |
|---|---|---|---|
| `--soft` | moves to commit 2 | unchanged | unchanged |
| `--mixed` | moves | reset to commit 2 | unchanged |
| `--hard` | moves | reset to commit 2 | reset to commit 2 |

Result of each (checked by running the three commands in real repositories):

| Mode | `git status --short` | Meaning |
|---|---|---|
| soft | `M  a.txt`, ` M b.txt`, `A  c.txt` | `c.txt` is "new" compared to commit 2 and still in the index; the staged edit stays staged |
| mixed | ` M a.txt`, ` M b.txt`, `?? c.txt` | the index forgot everything after commit 2; the files stay on disk |
| hard | (empty) | both places match commit 2; `c.txt` is deleted and the edits are discarded |

Answer:

```text
soft: tip=c-b staged=a.txt,c.txt unstaged=b.txt untracked=- files=a.txt,b.txt,c.txt
mixed: tip=c-b staged=- unstaged=a.txt,b.txt untracked=c.txt files=a.txt,b.txt,c.txt
hard: tip=c-b staged=- unstaged=- untracked=- files=a.txt,b.txt
```

In `hard`, two things are lost: the uncommitted edits to `a.txt` and `b.txt` (never recoverable: `reflog` knows only commits) and the file `c.txt` from the disk (commit 3 itself is still reachable from the reflog).

## Complexity

Not applicable.

## Another way

After each mode, run `git status --short` in a scratch repository, and compare the two columns with the three boxes.

## Why it matters

`--soft` is for "I committed too early", `--mixed` for "split this commit into smaller ones", `--hard` for "throw it all away". Picking wrong costs work.
