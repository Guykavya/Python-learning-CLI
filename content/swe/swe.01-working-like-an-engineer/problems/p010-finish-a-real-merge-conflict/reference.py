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
