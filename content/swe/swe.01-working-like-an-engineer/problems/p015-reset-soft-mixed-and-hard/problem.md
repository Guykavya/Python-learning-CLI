# `reset --soft`, `--mixed` and `--hard`

A repository has three commits, with these subjects and files:

| Commit | Subject | Adds the file |
|---|---|---|
| 1 | `c-a` | `a.txt` |
| 2 | `c-b` | `b.txt` |
| 3 | `c-c` | `c.txt` (this is `HEAD`) |

Two edits are pending: `a.txt` has an extra line that is **staged** (`git add a.txt` was run), and `b.txt` has an extra line that is **not staged**.

The same starting state is used three times; each time one command runs:

```text
soft : git reset --soft  HEAD~1
mixed: git reset --mixed HEAD~1
hard : git reset --hard  HEAD~1
```

After each command write the state in one line:

```text
<mode>: tip=<subject of the branch tip> staged=<list> unstaged=<list> untracked=<list> files=<list>
```

- `staged`: files that `git status --short` shows with a letter in the **first** column (`M`, `A`, `D`).
- `unstaged`: files with a letter in the **second** column (a modified tracked file, ` M`).
- `untracked`: files shown as `??`.
- `files`: the files that exist in the working tree.
- Every list is sorted alphabetically, separated by commas without spaces; write `-` for an empty list.

Do not run it. Think of the three places: repository, index, working tree (chapter sections 2.5 and 9.2).

## After you answer

1. In `soft`, why is `c.txt` still staged although the commit that added it is no longer in the branch?
2. In `mixed`, why is `a.txt` listed as unstaged and not staged, although you staged it before?
3. In `hard`, which two things are lost, and can `reflog` bring them back?
