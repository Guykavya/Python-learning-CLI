## Model answer

1. **`git commit --amend`** (opens the editor on the message). Safe because the commit is not pushed; if it were pushed, amending would rewrite shared history.
2. **`git revert <commit>`**: it adds a new commit that undoes the bad one. `reset` or `amend` would rewrite history that others already have, and their copies would diverge.
3. **`git reflog`** to find the hash `HEAD` had before the reset, then `git branch rescue <hash>` (or `git reset --hard <hash>`). The commits are not deleted at once; the reflog remembers them for a while. Do not run `gc` or wait months.
4. **`git restore config.py`**: it puts the committed version back. Be careful: the edits are lost for good, and `reflog` cannot save uncommitted work.
5. **`git restore --staged secrets.txt`**: it removes the file from the index and leaves it on disk. Do not commit it; a secret in history stays there and must then be revoked. Also add it to `.gitignore`.
6. **`git switch -c new-branch`** at the current tip, then move `main` back with `git branch -f main <old hash>` (or `git switch main` and `git reset --hard <old hash>`). The commits stay safe on the new branch. Do not copy the files by hand.
7. **`git stash`** (and `git stash pop` later). A throwaway commit full of half-done work, or a `reset --hard`, would pollute the history or lose it.
8. **`git reset --soft HEAD~1`**: the branch moves back one commit and the changes stay staged. `--hard` would discard them; `--mixed` would unstage them.

**Checklist: your answer should mention**
- [ ] `commit --amend` for an unpushed commit message
- [ ] `revert` for a pushed commit; never rewrite shared history
- [ ] `reflog` to recover a commit lost after `reset --hard`
- [ ] `restore` throws edits away for good; `restore --staged` only unstages
- [ ] a branch at the tip saves commits made on the wrong branch
- [ ] `stash` for unfinished work; `reset --soft` keeps changes staged
