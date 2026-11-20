# Follow the sticky notes

A branch is a sticky note on a commit; `HEAD` says which note you are standing on (chapter sections 2.3 and 2.4).

A new repository has one commit, named `A`, and one branch, `main`. `HEAD` is on `main`. Then these ten commands run, one after the other. `git commit` commands create an empty commit whose message is its **name**, so the new commit's name is the letter after `-m`.

```text
 1. git switch -c feature
 2. git commit --allow-empty -m B
 3. git commit --allow-empty -m C
 4. git switch main
 5. git merge feature
 6. git switch feature
 7. git commit --allow-empty -m D
 8. git switch main
 9. git merge --no-ff feature -m E
10. git branch -d feature
```

After **each** command write: the branch `HEAD` is on, the commit each branch points to (its letter), and `-` for a branch that does not exist (yet, or any more).

Write your answer in `answer.txt`, one line per command, exactly like this:

```text
1: HEAD=<branch> main=<letter> feature=<letter or ->
```

Do not run it.

## After you answer

1. Command 5 created no new commit. Why? (Chapter section 5.4.)
2. What are the two parents of `E`?
3. After command 10, is commit `D` lost? How can you reach it?
