## Hint 1

Two questions sort almost every case: is the commit **shared** (pushed)? And do you want to keep the **changes** or throw them away?

## Hint 2

Shared commits are never rewritten: you add a new commit that undoes them (`revert`). Unshared commits can be rewritten (`amend`, `reset`). A lost commit is usually not lost: where does git keep a log of where `HEAD` has been?

## Hint 3

Match: 1 `commit --amend`; 2 `revert`; 3 `reflog` then `branch`/`reset` to the old hash; 4 `restore config.py`; 5 `restore --staged`; 6 create a branch at the tip, then move `main` back; 7 `stash`; 8 `reset --soft HEAD~1`.
