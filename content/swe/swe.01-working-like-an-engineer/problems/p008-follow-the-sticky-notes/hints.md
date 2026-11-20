## Hint 1

Draw the commits as circles in a row and the two sticky notes as flags. `git switch -c feature` makes a **new** flag on the commit you are standing on, and `HEAD` moves to it. It does not create a commit.

## Hint 2

A new commit is added after the commit under `HEAD`'s branch, and **only that branch's flag** moves forward. `git switch` moves `HEAD`, not any flag.

## Hint 3

Command 5: `main` is on `A`, `feature` is on `C`, and `A` is an ancestor of `C`: a fast-forward, so the `main` flag just jumps to `C`. Command 9: `main` is on `C` and `feature` is on `D`, a child of `C`; a fast-forward would be possible, but `--no-ff` forces a new commit `E` with parents `C` and `D`, and `main` moves to `E`.
