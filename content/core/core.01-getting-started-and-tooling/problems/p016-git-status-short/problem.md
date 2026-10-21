# Reading git status

Predict the output of every `git status --short` in this session. All other
commands print nothing (`-q` means quiet).

```bash
$ mkdir diary && cd diary
$ git init -q
$ echo "Day 1" > notes.txt
$ git status --short          # (1)
$ git add notes.txt
$ git status --short          # (2)
$ git commit -q -m "Start diary"
$ git status --short          # (3)
$ echo "Day 2" >> notes.txt
$ git status --short          # (4)
$ git add notes.txt
$ git status --short          # (5)
$ echo "draft" > todo.txt
$ git status --short          # (6)
```

Write the outputs in `answer.txt`, in order, one line per output line.

- When a `git status --short` prints **nothing**, write `(clean)` on its own line.
- **Spaces matter.** Short status uses two columns before the file name: left
  is the staging area, right is the working folder. For example, `A  x.py` has
  `A`, then two spaces.

**Format example**

```
?? something.txt
(clean)
```
