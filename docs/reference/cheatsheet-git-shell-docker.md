# Git, shell and Docker cheat sheet

## Git
```text
git status / git diff / git diff --staged
git add -p                 stage in pieces
git commit -m "message"
git switch -c feature      new branch      git switch main
git log --oneline --graph --all
git restore file           discard changes (cannot be undone)
git stash / git stash pop
git rebase main            replay your branch on top of main (never on shared history)
git revert <sha>           undo a commit with a new commit (safe on shared branches)
git reflog                 find "lost" commits
```
Commit messages: imperative, one line under 72 characters, then why. Never commit secrets: if you did, rotate the key.

## Shell (Linux / macOS; PowerShell equivalent in brackets)
```text
pwd  ls -la  cd dir          [Get-Location, Get-ChildItem]
cat f  head -n 5 f  tail -f f  [Get-Content]
grep -rn "text" .            [Select-String -Path * -Pattern]
find . -name "*.py"
cmd1 | cmd2     cmd > out.txt     cmd >> out.txt     cmd 2>&1
export NAME=value            [$env:NAME = "value"]
```
Quote variables (`"$f"`) so spaces do not split them.

## Docker
```text
docker build -t app:1 .
docker run --rm -p 8000:8000 -e KEY=value app:1
docker ps  /  docker logs -f <name>  /  docker exec -it <name> sh
docker compose up -d  /  docker compose down
docker image prune        removes only unused images; do not run machine-wide prune on a shared machine
```
Dockerfile habits: small base image, copy `requirements.txt` first (layer cache), run as a non-root user, one process per container, a `HEALTHCHECK`.
