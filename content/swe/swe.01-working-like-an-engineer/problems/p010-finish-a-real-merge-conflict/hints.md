## Hint 1

How does git remember that a merge is unfinished? Look inside the `.git` folder of a repository during a conflict: a file named `MERGE_HEAD` holds the commit being merged.

## Hint 2

Order of operations matters: validate first (merge in progress, no markers), then write, then `git add`, then check what is still unmerged, and only then commit. `subprocess.run([...], cwd=repo, capture_output=True, text=True, check=True)` runs a command in the repository.

## Hint 3

```text
if not (repo/.git/MERGE_HEAD).exists(): raise RuntimeError("no merge in progress")
if any line of resolved_text starts with "<<<<<<<" or ">>>>>>>": raise ValueError
write bytes of the text (utf-8)
git add -- path
unmerged = git diff --name-only --diff-filter=U  -> split lines
if unmerged: raise RuntimeError("unresolved files remain: ...")
git commit --no-edit
```
