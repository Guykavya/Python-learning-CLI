# Branches and history

Predict everything this session prints. Start in a new empty folder. Commands
marked `-q` (quiet) print nothing.

```bash
$ git init -q -b main
$ echo "v1" > app.py
$ git add app.py
$ git commit -q -m "First version"
$ git branch feature
$ git switch -q feature
$ echo "v2" > app.py
$ git commit -q -am "Try v2"
$ git branch
$ cat app.py
$ git switch -q main
$ cat app.py
$ git log --format=%s
$ git log --format=%s feature
$ git diff --name-only main feature
```

Notes:

- `git init -b main` names the first branch `main`.
- `git commit -am` stages every already-tracked file that changed, then commits.
- `git branch` lists branches in alphabetical order. The current branch is
  marked with `* `; others start with two spaces.
- `git log --format=%s` prints only commit messages, newest first. Giving a
  branch name shows that branch's history instead of the current one.
- `git diff --name-only A B` lists the files that differ between two branches.

Write the output in `answer.txt`, one line per output line. Leading spaces
matter.
