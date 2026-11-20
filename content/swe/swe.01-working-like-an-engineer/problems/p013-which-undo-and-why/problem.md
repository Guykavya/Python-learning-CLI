# Which undo, and why?

Chapter section 9.1 has a decision table. For each of the eight situations below, write in `answer.md`: **the command you would use**, and **one sentence on why the risky alternative is wrong** (or what could go wrong).

1. You made a typo in the message of your **last commit**, which you have **not pushed**.
2. A commit that broke production is **already pushed** and your teammates have pulled it.
3. You ran `git reset --hard HEAD~3` and now realise you needed one of those commits.
4. You edited `config.py` badly and want the **committed version back**; the edits are not worth keeping.
5. You staged `secrets.txt` by mistake, **before committing**.
6. You made two commits on `main` but they belong on a **new branch**, and nothing is pushed.
7. You are in the middle of a feature and an urgent bug report arrives; your changes are **not ready to commit**.
8. You committed too early: you want the last commit **undone but its changes kept staged**, so you can add more.

Use the commands of the chapter: `commit --amend`, `revert`, `reflog` and `branch`, `restore`, `restore --staged`, `reset --soft`, `stash`, `switch -c` and `reset`. Give your reasons in your own words.
