## Approach

Walk the list and update the result list:

| Line | Effect on the result |
|---|---|
| `pick A` | `[A]` |
| `reword B` | `[A, B("Add login form")]` |
| `fixup C` | `C` melted into `B`: `[A, B+C]` |
| `pick E` | `[A, B+C, E]` |
| `squash D` | `D` melted into `E`: `[A, B+C, E+D]` |
| `drop F` | `F` disappears |

Final history:

```text
Add base | A
Add login form | B C
Add docs | E D
```

This was checked by running exactly this rebase in a real repository: the three commits had the files `A.txt`; `B.txt` and `C.txt`; `D.txt` and `E.txt`. The `Add docs` commit's message was `Add docs` followed by `Add search` in the body (the squashed message), so its subject is `Add docs`.

Six commits became three: `C` and `D` are not separate commits any more, and `F` is gone with its file.

## Complexity

Not applicable.

## Another way

The same result as a picture: before, a row `A B C D E F`; after, a row of three blocks `[A] [B C] [E D]`. Write the blocks on paper before answering.

## Why it matters

Before opening a pull request you often `squash` your work-in-progress commits into a few meaningful ones. Knowing exactly where each commit goes (and that the to-do list can reorder them) avoids surprises. Never do this to commits that others already have (chapter section 7.3).
