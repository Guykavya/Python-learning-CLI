## Approach

```python
import subprocess
from pathlib import Path


def _git(repo, *args):
    return subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True, check=True)


def finish_merge(repo, path, resolved_text):
    repo = Path(repo)
    if not (repo / ".git" / "MERGE_HEAD").exists():
        raise RuntimeError("no merge in progress")
    for line in resolved_text.split("\n"):
        if line.startswith("<<<<<<<") or line.startswith(">>>>>>>"):
            raise ValueError("the resolved text still contains conflict markers")
    (repo / path).write_bytes(resolved_text.encode("utf-8"))
    _git(repo, "add", "--", path)
    left = _git(repo, "diff", "--name-only", "--diff-filter=U").stdout.split()
    if left:
        raise RuntimeError("unresolved files remain: " + ", ".join(left))
    _git(repo, "commit", "--no-edit")
```

Why write **bytes**: `write_text` on Windows converts `\n` to `\r\n`, and the content would not equal what the caller passed. Why check for unmerged files **after** `git add`: the add is what marks this file resolved; `--diff-filter=U` then lists only the files that are still in the "both modified" state. Why `commit --no-edit`: git stored the merge message in `.git/MERGE_MSG`; the command uses it and does not open an editor.

Example: with two conflicted files, the first call writes and adds `prices.py`, finds `drinks.py` still unmerged and raises; the merge stays open. After the second call the commit is created and `MERGE_HEAD` is gone.

## Complexity

A few git commands; no loops over history.

## Another way

`git checkout --ours -- path` or `git merge --continue` (git 2.12 and newer) would also finish a merge; `merge --continue` refuses with an error when files are unresolved. Scripts that must check things themselves, as here, prefer the explicit commands.

## Why it matters

Scripting git through its commands and its files (`MERGE_HEAD`) is how tools like pre-commit hooks and release scripts work. The two checks (markers and unmerged files) are the same safety net a CI job would add.
