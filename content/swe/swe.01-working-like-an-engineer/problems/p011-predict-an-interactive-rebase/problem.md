# Predict an interactive rebase

A branch has six commits, oldest first. Each commit adds one file named after its letter.

| Letter | Subject | File |
|---|---|---|
| A | `Add base` | `A.txt` |
| B | `Add login` | `B.txt` |
| C | `Fix typo in login` | `C.txt` |
| D | `Add search` | `D.txt` |
| E | `Add docs` | `E.txt` |
| F | `wip` | `F.txt` |

You run `git rebase -i --root` and edit the to-do list into this (git runs it from top to bottom):

```text
pick   A
reword B
fixup  C
pick   E
squash D
drop   F
```

When git stops to let you write the new message for `B` (because of `reword`), you type `Add login form` as the only line. When git offers the combined message for the `squash`, you leave it as git proposes it. (Chapter sections 7.5 and 7.6: a `squash` message starts with the subject of the commit it is squashed **into**.)

Predict the **final history**, oldest first. For each new commit write its **subject** and which old commits are inside it, **in the order git applied them**.

Write your answer in `answer.txt`, one line per final commit:

```text
<subject> | <letters separated by spaces>
```

Do not run it.

## How to work

1. Go down the list. `pick` starts a new commit. `fixup` and `squash` **meld** a commit into the commit just above them in the *result*. `reword` is a `pick` with a new message. `drop` throws the commit away.
2. Note that the list **reorders**: `E` is applied before `D`.
3. A `fixup` discards its own message; a `squash` keeps the subject of the target (it appends the other message to the body).

## After you answer

1. How many commits are in the new history, and which old commit is gone completely?
2. Which of the final commits contains the changes of `D`?
3. Why can the reordering `E` before `D` cause a conflict in a real project, although not here?
