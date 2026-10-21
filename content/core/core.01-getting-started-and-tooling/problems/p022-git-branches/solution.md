## Walkthrough

| Command | Output | Why |
|---|---|---|
| `git branch` | `* feature` and `  main` | alphabetical; `*` marks the current branch, which is `feature` |
| `cat app.py` | `v2` | the working folder matches `feature` |
| `git switch -q main`, `cat app.py` | `v1` | switching rewrote `app.py` to `main`'s snapshot |
| `git log --format=%s` | `First version` | `main` has only one commit |
| `git log --format=%s feature` | `Try v2`, `First version` | newest first; `feature` began from `main`'s commit |
| `git diff --name-only main feature` | `app.py` | the only file that differs |

## Under the hood

`git branch feature` just created a pointer to the `First version` commit. The
commit `Try v2` moved the `feature` pointer forward. `main` stayed put. Each
commit points to its parent, so `feature`'s history is `Try v2`, then
`First version`.
