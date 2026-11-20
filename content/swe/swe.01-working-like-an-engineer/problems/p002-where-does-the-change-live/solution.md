## Approach

Write the three boxes after every command (commit / index / working tree). A diff exists when the two boxes it compares differ.

| After command | commit | index | working tree | `git diff` | `git diff --staged` |
|---|---|---|---|---|---|
| start | v1 | v1 | v1 | | |
| 1 `echo v2` | v1 | v1 | v2 | index vs tree: differ, **yes** | commit vs index: same, **no** |
| 2 `git add` | v1 | v2 | v2 | no | **yes** |
| 3 `echo v3` | v1 | v2 | v3 | yes | yes |
| 4 `restore --staged` | v1 | v1 | v3 | yes | no |
| 5 `git add` | v1 | v3 | v3 | no | yes |
| 6 `git commit` | v3 | v3 | v3 | no | no |
| 7 `echo v4` | v3 | v3 | v4 | yes | no |

The answer was produced by running exactly these commands in a real repository.

Command 4 does not touch the file on disk: `git restore --staged` copies the **committed** version into the **index** only, so the staged change disappears while the working file still says `v3`.

## Complexity

Not applicable.

## Another way

Run `git status --short` after each command. The two columns of its output are exactly these two diffs: first column = `diff --staged`, second column = `diff`.
