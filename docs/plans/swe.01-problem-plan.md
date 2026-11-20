# Problem plan: swe.01 Working like an engineer (20 problems)

Rules: [README.md](README.md) (shared rules R1–R5) and [dsa.07-problem-plan.md](dsa.07-problem-plan.md) (table format).
Function style (`from solution import f`). Ids `swe.01.p001`…`p020`, folder `pNNN-slug`.

**Mix:** 8 drill, 6 applied, 4 deep, 2 challenge. **Kinds:** 13 code, 4 trace, 3 explain.
**assessment:** explain = p013, trace = p008, fix = p018, build = p020.
**★ core set (write first):** p001, p003, p008, p009, p010, p013, p016, p017, p020 (covers both outcomes: resolve a conflict and keep history clean; a project others can install and test in minutes).

**Testing notes**
- Most git problems are **pure Python over git's text output** (porcelain status, `git log --format=...`, conflict markers, rebase todo lists): the test passes the text in, no git needed. This is fast and identical on every OS.
- Only p006 (cross-check), p010 and p020 run real git, always inside `tmp_path`, through a helper in `conftest.py`:
  `git(repo, *args)` = `subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", "-c", "init.defaultBranch=main", "-c", "commit.gpgsign=false", "-c", "core.autocrlf=false", *args], cwd=repo, capture_output=True, text=True, check=True)`.
  The first test asserts `shutil.which("git")` with the message "git is not installed; swe.01 §3 shows how". Never touch the course repository.
- The commit graph is passed as `{sha: [parent_sha, ...]}` plus `{branch: sha}`; the chapter's picture of "a branch is a sticky note" (Ch. 2.3) is exactly this model.
- Subprocess children use `sys.executable` (R5). p020's inner pytest run takes ~2 s.

## A. The git model (Ch. 2–3)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 1 | Read `git status --porcelain` ✅ | drill | code | `parse_status(text)` → `{"staged": [...], "modified": [...], "untracked": [...], "deleted": [...]}` from `XY path` lines; renames `R  old -> new`; a file both staged and modified appears in both lists; empty text → all empty |
| 2 | Where does the change live? ✅ | drill | trace | `⚠ HAND-TRACE` 7 commands (edit, `add`, edit again, `commit`, `restore --staged`, …); for each step write what `git diff`, `git diff --staged` show (`yes`/`no`) for the file; answer format pinned in `problem.md` |
| 3 | The commit graph from `git log` ✅ | applied | code | input = lines of `git log --all --format="%h %p"`; `parse_graph(text)` → parent map; `merge_commits(graph)`, `ancestors(graph, sha)` (includes itself); root commit has no parents; test graph with two merges |
| 4 | Fast-forward or real merge? ✅ | applied | code | `merge_kind(graph, current, other)` → `"up-to-date"`, `"fast-forward"` or `"merge"` using the ancestor test; message names the case when `other` is already an ancestor (Ch. 5.4–5.5) |

## B. Commits and `.gitignore` (Ch. 4)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 5 | A commit message linter ✅ | drill | code | `lint_message(msg)` → list of problems: subject > 50 chars, ends with `.`, missing blank line before body, body line > 72 chars, empty message; a perfect message → `[]`; each rule tested alone so the message names the rule |
| 6 | A small `.gitignore` matcher ✅ | deep | code | `is_ignored(path, patterns)`: `*`, `**`, leading `/` anchors, trailing `/` only matches directories (paths ending in `/`), `!` re-includes, last matching rule wins, `#` comments and blank lines; 25 hand-worked cases; an extra test (skipped if git is missing) compares 10 cases with `git check-ignore --no-index` in `tmp_path` |
| 7 | What makes a good commit? ✅ | drill | explain | two histories of the same change (one "wip/fix/stuff", one atomic); explain which one helps `revert`, `bisect` and review and why; checklist: atomic, builds and tests pass, message says why, no generated files |

## C. Branches, merges and conflicts (Ch. 5–6)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 8 | Follow the sticky notes ✅ | applied | trace | `assessment = "trace"`. `⚠ HAND-TRACE` a 10-command script (`switch -c`, `commit`, `switch`, `merge` fast-forward, `merge --no-ff`, `branch -d`); after each command write `HEAD`, the branch it points to and the commit letter of each branch (`A`,`B`,…); pinned answer format |
| 9 | Resolve conflict markers ✅ | applied | code | `resolve(text, choose)` reads a file with `<<<<<<< ours` / `=======` / `>>>>>>> theirs` blocks; `choose` is `"ours"`, `"theirs"`, `"both"` or a function `(ours_lines, theirs_lines) -> lines`; several blocks in one file; a file with no markers is unchanged; unbalanced markers raise `ValueError` naming the line |
| 10 | Finish a real merge conflict ✅ | challenge | code | the test builds a real conflict with git in `tmp_path` (two branches edit line 3 of `prices.py`); `finish_merge(repo, path, resolved_text)` writes the file, `git add`s it and commits; checks: `git status --porcelain` empty, `HEAD` has 2 parents, no marker left in any tracked file, the file content equals `resolved_text`; second test: calling it when no merge is in progress raises `RuntimeError` ("no merge in progress": check `.git/MERGE_HEAD`) |

## D. Rewriting and undoing history (Ch. 7–9)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 11 | Predict an interactive rebase ✅ | deep | trace | `⚠ HAND-TRACE` a todo list over 6 commits with `pick`, `reword`, `squash`, `fixup`, `drop` and one reordering; write the final list of commit subjects, oldest first, and which old commits each one contains |
| 12 | Apply a todo list (with `--autosquash`) ✅ | deep | code | commits are `(sha, subject)`; `autosquash(commits)` moves each `fixup! X` right after `X` and marks it `fixup`; `apply_todo(commits, todo)` returns the new subjects; `squash`/`fixup` as the first line raise `ValueError` (git refuses too); a `fixup!` with no target stays a `pick` |
| 13 | Which undo, and why? ✅ | drill | explain | `assessment = "explain"`. 8 situations (typo in the last unpushed commit, a pushed commit that broke prod, a lost branch after `reset --hard`, unstaged edits to throw away, …); name the command (`commit --amend`, `revert`, `reflog` + `branch`, `restore`, `reset --soft`, `stash`) and say why the risky alternative is wrong; checklist in `answer.md` uses Ch. 9.1's decision table |
| 14 | `git bisect` by hand ✅ | drill | code | `first_bad(commits, is_bad)` with the history oldest→newest, first known good and last known bad; binary search; the test counts calls to `is_bad` (≤ ⌈log₂ n⌉ + 1) and checks n = 2, 3, 1,000; message "you tested every commit: that is a linear search" |
| 15 | `reset --soft`, `--mixed`, `--hard` ✅ | drill | trace | `⚠ HAND-TRACE` the same starting state (3 commits, one staged and one unstaged edit) after each of the three resets to `HEAD~1`; write the branch tip, what is staged, what is in the working tree |

## E. Project structure and tooling (Ch. 11–14)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 16 | Check a `pyproject.toml` ✅ | applied | code | `check_pyproject(text, files)` with `tomllib`; `files` is a list of paths in the repo; returns problems: missing `[project] name/version/requires-python`, package not under `src/`, `testpaths` folder missing, `ruff` line length set twice, dependency without a lower bound; a correct file (the chapter's Ch. 17.4) → `[]` |
| 17 | A pure-Python task runner ✅ | applied | code | `main(argv, run)` like the chapter's `tasks.py` (Ch. 13.4, 17.5); `run(cmd) -> int` is injected, the test records commands; tasks `test`, `lint`, `types`, `check`; `check` runs lint → types → test and stops at the first non-zero; unknown task → prints the list, returns 2; commands use `sys.executable -m ...` not `python` |
| 18 | Fix the runner that always says OK ✅ | drill | code | `assessment = "fix"`. Given `tasks.py` with three bugs: ignores return codes, calls `"python"` by name, `check` runs tests before lint; the tests describe the behaviour of p017 in miniature; mistakes.md explains why CI went green with failing tests |

## F. Documentation, review and the template (Ch. 15–18)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 19 | Review a pull request ✅ | deep | explain | a 40-line diff (a new `discount()` with a float-money bug, a missing test, a renamed public function, a style nit); write 4 review comments, each labelled blocking/suggestion/nit, saying why and offering a fix; checklist: finds the money bug and the API break, kind tone (Ch. 16.5), nit marked as a nit |
| 20 | The professional project template ✅ | challenge | code | `assessment = "build"`. `make_project(root, name)` writes the template of Ch. 17: `src/<name>/__init__.py`, `tests/test_<name>.py`, `pyproject.toml`, `tasks.py`, `README.md` (Install/Use/Develop sections), `CHANGELOG.md` (`## [Unreleased]`), `.gitignore`; tests: files exist, `tomllib` parses the pyproject and its name matches, README has the sections, `.gitignore` ignores `__pycache__/` and `.venv/` (reuse p006 cases inline), and **the fresh-clone test**: run `sys.executable -m pytest -q` inside the new project (with `PYTHONPATH=src`) in a subprocess and require exit 0; invalid names (`"my-proj"`, `"1abc"`) raise `ValueError` |

## Counts check
Written 2026-11-19, all 20 validated (Sonnet, main session). Deviations from the table: p016 checks 'ruff configured twice (pyproject.toml and ruff.toml)' instead of 'line length set twice' (TOML cannot repeat a key); p012 uses tuple steps `(cmd, sha[, new_subject])` and exact-subject matching for autosquash; p002/p008/p011/p015 expected answers were produced by running the real git commands (git 2.53) and then pinned; p006's git cross-check covers 10 cases (all 33 hand cases also agree with git); p020's inner pytest run uses `-o addopts=`. No separate conftest.py: each git test file carries its own `git()` helper.

Tiers: drill = 1, 2, 5, 7, 13, 14, 15, 18 is 8; applied = 3, 4, 8, 9, 16, 17 is 6; deep = 6, 11, 12, 19 is 4; challenge = 10, 20 is 2. Total 20 (8/6/4/2: close to the 1/3 rule; acceptable for a tooling module).
Kinds: trace 2, 8, 11, 15 (4); explain 7, 13, 19 (3); code 13. One assessment each: explain p013, trace p008, fix p018, build p020.

## Risks and open questions

- **git versions:** messages differ between git versions; tests never compare git's human messages, only porcelain output, exit codes and file contents.
- p010/p020 need git on the machine; Windows git may set `core.autocrlf=true` globally, which is why the helper forces `core.autocrlf=false`.
- p006's matcher is a teaching subset; `problem.md` lists exactly which `.gitignore` rules are in scope so the git cross-check only uses those.
- Makefile (Ch. 13.2) and pre-commit (Ch. 14) are not tested by running `make`/`pre-commit` (not installed on Windows); they appear in hints and in p017/p018's design.
