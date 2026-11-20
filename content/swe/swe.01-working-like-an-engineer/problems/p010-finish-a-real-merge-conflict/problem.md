# Finish a real merge conflict

Automate the last steps of chapter section 6.4. Write

```python
finish_merge(repo, path, resolved_text)
```

where `repo` is the path of a repository that is **in the middle of a conflicted merge**, `path` is a file of that repository (relative path) and `resolved_text` is its final content. The function:

1. raises `RuntimeError` (message containing `no merge in progress`) if there is no merge going on: git marks a merge in progress with the file `.git/MERGE_HEAD`;
2. raises `ValueError` if `resolved_text` still has a line beginning with `<<<<<<<` or `>>>>>>>`, **before touching anything**;
3. writes `resolved_text` to the file exactly as given (UTF-8, no newline translation);
4. runs `git add` on it;
5. if **other files are still unmerged** (`git diff --name-only --diff-filter=U` is not empty) raises `RuntimeError` whose message names them, and leaves the merge in progress;
6. otherwise commits with `git commit --no-edit` (git has already prepared the merge message), which creates a commit with **two parents**.

Use `subprocess` with the `git` command, `cwd=repo`. The tests create real repositories in a temporary folder; they never touch your course repository. Needs `git` installed.

## Example

After `git merge feature` stopped with a conflict in `prices.py`:

```python
finish_merge("/tmp/shop", "prices.py", "TEA = 10\nCOFFEE = 20\nCAKE = 40\nJUICE = 40\n")
# afterwards: git status is clean, HEAD has two parents
```
