# Where does the change live?

A repository has one committed file, `app.py`, containing the line `v1`. A clean checkout: `git status` is empty.

Then these commands run, **one after the other**:

```text
1. echo v2 > app.py
2. git add app.py
3. echo v3 > app.py
4. git restore --staged app.py
5. git add app.py
6. git commit -m "Update app"
7. echo v4 > app.py
```

After **each** command, would these two commands show something?

- `git diff app.py` (working tree compared with the index): answer `yes` if it prints a difference, `no` if it prints nothing.
- `git diff --staged app.py` (index compared with the last commit): the same.

Do not run it. Think of the three places of chapter section 2.5: working tree, index, repository.

Write your answer in `answer.txt`, one line per command, exactly in the form

```text
1: diff=yes staged=no
```

(your own values).

## After you answer

1. After command 3, `app.py` has a staged version and a different working version. What does each of the two diffs compare?
2. Command 4 does not change the file on disk. What does it change?
3. After command 6 both diffs are empty. What does `app.py` contain at that moment, and what is in each of the three places after command 7?
