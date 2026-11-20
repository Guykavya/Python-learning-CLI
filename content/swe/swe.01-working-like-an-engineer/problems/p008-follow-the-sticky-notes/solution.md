## Approach

Keep two things: the commit row, and the positions of the flags.

| After | Commits | Flags and HEAD |
|---|---|---|
| start | A | main on A, HEAD on main |
| 1 | A | main on A, **feature on A**, HEAD on feature |
| 2 | A, B | feature on B |
| 3 | A, B, C | feature on C |
| 4 | | HEAD on main (flags do not move) |
| 5 | | fast-forward: main jumps to C |
| 6 | | HEAD on feature |
| 7 | A, B, C, D | feature on D (main stays on C) |
| 8 | | HEAD on main |
| 9 | adds E | `--no-ff`: new commit E with parents C and D; main on E |
| 10 | | the `feature` flag is removed |

The answer was produced by running exactly these commands in a real repository.

`D` is not lost after command 10: it is a parent of `E`, so it is reachable from `main`. Deleting a branch deletes only the sticky note (git refused to delete it if its commits were not merged; `-d` checks that, `-D` does not).

## Complexity

Not applicable.

## Another way

`git log --oneline --graph --all` draws exactly this picture and shows every flag; run it after each step in a practice repository.
