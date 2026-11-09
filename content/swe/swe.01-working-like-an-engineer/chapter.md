# Chapter 1 (SWE): Working like an engineer

Until now you wrote programs. A program is something that runs on **your** computer, today. A **project** is something else: code that other people (and you, six months from now) can **install**, **test**, **change** and **trust**. The difference is not cleverness. It is habits: how you save history, how you lay out folders, how you automate boring commands, how you explain your work, and how you read other people's work.

This chapter teaches those habits. It is the first chapter of the *Software Engineering* track, and it builds on **core.13** (modules, packages, virtual environments, `pyproject.toml`). You do not need to re-learn those. Here we use them.

By the end you reach two outcomes:

- You can **resolve a merge conflict** and **keep a clean history**.
- You can **set up a new project that others can install and test in minutes**.

And the project at the end is a **professional project template** that you reuse for every later project in this course.

Along the way you will answer these questions:

- What is a commit, really? What is a branch? What is `HEAD`? Why is git called a "graph"?
- What are the working tree, the index (staging area) and the repository, and why does git have all three?
- What is the difference between **merge** and **rebase**, and when must you never rebase?
- How do you fix a mistake: a wrong commit message, a commit on the wrong branch, a deleted branch, a `reset --hard` that you regret?
- What does a merge conflict look like, and what exactly do you do about it?
- What is GitHub flow? What is a pull request for?
- Why do many projects put their code in `src/`? What goes in `pyproject.toml`?
- How do you give your project one-word commands (`make test`) that also work on Windows?
- What belongs in a README? What is a good code review, and how do you take one without getting upset?

**A note on how examples are shown.** Every command block in this chapter was **really run** with **git 2.53** and **Python 3.14** on Linux, inside a throwaway practice folder. The output you see is the real output. To make the outputs identical every time, the test machine used a fixed identity (`Ada Learner <ada@example.com>`), a fixed branch name (`main`), and a clock that moves one hour per command. This has one consequence you must understand now:

> **Commit hashes (the letters and digits like `a1b2c3d`) will be different on your machine.** A hash is computed from the content, the author, the date and the parent. Your name and your clock are different, so your hashes are different. Always read the *shape* of the output, never copy a hash from the book. Dates, author names and paths are machine-specific in the same way. Paths are shown as `/home/you/work`.

**Offline by design.** Everything you must *run* needs only `git`, `python`, and (optionally) `make`. We even practise "remote" work with a **local bare repository** acting as a fake GitHub. Things that need an outside account or the network (GitHub itself, a CI service, installing `pre-commit` or `ruff` from the internet) are placed in clearly marked **"Try it on your machine"** boxes. In those boxes the commands are exact, and the output is described but not captured.

**Check your tools first.**

```text
$ git --version
git version 2.53.0
$ python --version
Python 3.14.4
$ make --version | head -1
GNU Make 4.4.1
```

If your versions are a little different, that is fine. If `make` is missing (common on Windows), do not worry: section 13 gives a pure-Python task runner that does the same job, and every runnable example there uses it.

**Safety rule for this whole chapter.** Never practise git commands inside your real course folder. Make a practice area:

```text
$ mkdir -p ~/practice && cd ~/practice
```

Every example below starts in an empty folder inside it. If you break something, delete the folder and start again. Breaking things *on purpose* in a safe place is the best way to learn git.

## Table of contents

1. [Why engineering habits](#1-why-engineering-habits)
2. [The git mental model](#2-the-git-mental-model)
3. [Your first repository](#3-your-first-repository)
4. [Good commits, messages and `.gitignore`](#4-good-commits-messages-and-gitignore)
5. [Branches and merging](#5-branches-and-merging)
6. [Merge conflicts](#6-merge-conflicts)
7. [Rebase and interactive rebase](#7-rebase-and-interactive-rebase)
8. [`cherry-pick` and `stash`](#8-cherry-pick-and-stash)
9. [Undoing mistakes safely](#9-undoing-mistakes-safely)
10. [Remotes and GitHub flow](#10-remotes-and-github-flow)
11. [Project structure and the `src` layout](#11-project-structure-and-the-src-layout)
12. [`pyproject.toml`, pytest, ruff and mypy](#12-pyprojecttoml-pytest-ruff-and-mypy)
13. [Task runners: Makefile and pure Python](#13-task-runners-makefile-and-pure-python)
14. [Git hooks and pre-commit](#14-git-hooks-and-pre-commit)
15. [Writing documentation](#15-writing-documentation)
16. [Code review](#16-code-review)
17. [Project: the professional project template](#17-project-the-professional-project-template)
18. [The new-project checklist](#18-the-new-project-checklist)
19. [Common traps](#19-common-traps)
20. [Summary](#20-summary)

## 1. Why engineering habits

### 1.1 What goes wrong without them

Here is a story that happens to almost every beginner. You write a program that works. You want to add a feature. You copy the folder to `project_backup`, then `project_backup2`, then `project_final`, then `project_final_REAL`. Two weeks later you do not know which folder has the working version, or what changed between them. You send the code to a friend. She asks "how do I run it?" and you cannot remember which libraries you installed. She runs it, it fails, and your only answer is "it works on my machine".

Every habit in this chapter is a cure for one of those pains:

| Pain | Cure | Section |
|---|---|---|
| "Which folder is the real one? What changed?" | **Version control** (git) | 2 to 9 |
| "I want to try something risky" | **Branches** | 5 |
| "Two of us changed the same line" | **Merge and conflict resolution** | 6 |
| "I broke it and want yesterday's version" | **Undo tools** | 9 |
| "Where do I put the files?" | **Project layout** | 11 |
| "How do I run it?" | **pyproject, task runner, README** | 12, 13, 15 |
| "Is my change good?" | **Tests, linting, code review** | 12, 14, 16 |

### 1.2 The goal: boring and repeatable

A professional project feels **boring** to work in. You clone it, run one command to set up, one to test, one to check style. Everything works the same on every machine. That boredom is the result of a lot of careful work, and it is the thing that lets people focus on the interesting part: the code.

Think of a kitchen in a good restaurant. Every tool has a place. Every recipe is written down. Anyone can cook any dish. A messy home kitchen can produce one good meal; a professional kitchen can produce a thousand, every day, by different cooks. We are building the professional kitchen.

### 1.3 Two kinds of history

Git gives you two things that beginners mix up:

- **A safety net**: you can always go back.
- **A story**: the history is a document that explains *why* the code became what it is.

The safety net works even if your commits are messy. The story needs care. Much of this chapter is about the second one, because a clean, readable history is the thing teammates (and your future self) will thank you for.

## 2. The git mental model

Most people struggle with git because they memorise commands without a picture. Learn the picture first. The commands then become obvious.

### 2.1 A commit is a snapshot, not a difference

When you commit, git stores a **snapshot** of every tracked file at that moment, plus:

- who made it (author) and when,
- a **message**,
- a pointer to its **parent** commit (the one before it).

Each commit gets a name: a 40-character **hash** (SHA-1 or SHA-256 of its content) such as `3f786850e387550fdab836ed7e6dc881de23001b`. Humans use the first 7 characters. Because the hash is computed from the content *and* the parent's hash, **you cannot change a commit without changing its hash**, and you cannot change a commit without changing the hashes of all commits after it. This one fact explains why "rewriting history" is dangerous (section 7).

> Diffs (`git diff`, `git show`) are **calculated** on demand by comparing two snapshots. Git does not store changes; it stores states. (Internally it packs data cleverly, so it does not waste space.)

### 2.2 History is a graph (a DAG)

Because every commit points to its parent, commits form a chain. We draw it with the oldest on the left and arrows pointing back to the parent:

```text
A <-- B <-- C
```

When two lines of work are combined, a commit gets **two** parents. When work forks, one commit has **two children**. So the history is not a line but a graph with arrows and **no loops**: a **directed acyclic graph**, or DAG.

```text
A <-- B <-- C <-- F          (F has two parents: C and E)
       \         /
        D <-- E
```

You will draw graphs like this many times. They are the most useful tool for understanding what a command does.

### 2.3 A branch is just a sticky note

A **branch** is a name that points at one commit. That is all. It is a 41-byte file. Creating a branch costs nothing, which is why git users create them freely.

```text
A <-- B <-- C        <-- main
```

When you commit while on a branch, the sticky note **moves forward** to the new commit.

### 2.4 `HEAD`: where you are

`HEAD` is another pointer. It says "the commit (usually through a branch) that I am looking at right now". Normally `HEAD` points at a *branch*, and the branch points at a commit:

```text
HEAD --> main --> C
```

If you check out a commit directly, `HEAD` points at the commit itself. That is called a **detached HEAD**. It is not an error, but new commits are not on any branch, and are easy to lose (section 9 shows how to rescue them).

### 2.5 Three places: working tree, index, repository

Git keeps your files in three places. This is the thing beginners find strangest, and also the thing that makes git powerful.

```text
  working tree          index (staging area)         repository
  (files you edit)      (the next commit, drafted)   (committed history)

   edit files   --git add-->   staged   --git commit-->   new commit
                <--git restore--           <--git reset--
```

- **Working tree**: the real files in your folder. You edit them with your editor.
- **Index** (also called the **staging area**): a draft of your next commit. `git add` copies the current version of a file into it.
- **Repository**: the `.git` folder with all commits.

Why the middle step? Because it lets you **choose what goes in a commit**. You may have changed five files for two different reasons. With the index you can commit the first reason (two files), then the second (three files). Two small, clear commits instead of one confusing one.

The four states of a file therefore are: *untracked* (git has never seen it), *modified* (changed in the working tree), *staged* (copied into the index) and *committed*.

### 2.6 Commands as moves on the picture

Once you have the picture, each command is a move:

| Command | What it moves |
|---|---|
| `git add f` | working tree to index |
| `git commit` | index to a new commit; the current branch moves forward |
| `git switch b` | `HEAD` to branch `b`; working tree is updated |
| `git branch b` | creates a new sticky note at the current commit |
| `git merge b` | combines `b` into the current branch |
| `git reset` | moves the current branch (and maybe index, working tree) |
| `git restore f` | copies a file from the index or a commit into the working tree |

Keep this table in mind. Everything in this chapter is a variation.

## 3. Your first repository

### 3.1 Telling git who you are

Git puts your name and email into every commit. Set them once for the whole computer:

```text
$ git config --global user.name "Your Name"
$ git config --global user.email "you@example.com"
$ git config --global init.defaultBranch main
$ git config --global core.editor "code --wait"
$ git config --global alias.lg "log --oneline --graph --decorate --all"
```

(These commands change your global settings, which are in the file `~/.gitconfig`. The editor line is an example for VS Code; use `nano` or `vim` if you prefer. The `alias.lg` line creates a short command, `git lg`, that we use constantly.)

`init.defaultBranch main` makes new repositories start on a branch called `main` (older git used `master`). In this book every example uses `main`.

> **Machine-specific.** The output of this book's examples used the identity `Ada Learner <ada@example.com>`. Yours will show your own name.

### 3.2 `git init`, `status`, `add`, `commit`

Make a folder and turn it into a repository:

```text
$ mkdir shop
$ cd shop
$ git init
Initialized empty Git repository in /home/you/work/shop/.git/
$ git status
On branch main

No commits yet

nothing to commit (create/copy files and use "git add" to track)
```

`git init` created a hidden folder `.git/`. That folder **is** the repository: delete it and the history is gone, but your files stay. Never edit files inside `.git/` by hand.

Now create a file and watch git notice:

```python
"""Price helpers."""

TAX_RATE = 0.18


def with_tax(price):
    return round(price * (1 + TAX_RATE), 2)
```

```text
$ git status
On branch main

No commits yet

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	price.py

nothing added to commit but untracked files present (use "git add" to track)
$ git add price.py
$ git status
On branch main

No commits yet

Changes to be committed:
  (use "git rm --cached <file>..." to unstage)
	new file:   price.py
$ git commit -m "Add with_tax helper"
[main (root-commit) d45c12d] Add with_tax helper
 1 file changed, 7 insertions(+)
 create mode 100644 price.py
$ git status
On branch main
nothing to commit, working tree clean
```

Read the four `status` outputs as the four states: *untracked*, *staged* ("Changes to be committed"), and finally *clean*. The line `[main (root-commit) ...]` shows the branch (`main`), that this is the first commit (`root-commit`) and the short hash. Your hash will differ.

### 3.3 Seeing the history

```text
$ git log
commit d45c12df07f9f83b1f9098b852af04d98c990a3a
Author: Ada Learner <ada@example.com>
Date:   Thu Jan 1 07:00:00 2026 +0000

    Add with_tax helper
$ git log --oneline
d45c12d Add with_tax helper
$ git show --stat HEAD
commit d45c12df07f9f83b1f9098b852af04d98c990a3a
Author: Ada Learner <ada@example.com>
Date:   Thu Jan 1 07:00:00 2026 +0000

    Add with_tax helper

 price.py | 7 +++++++
 1 file changed, 7 insertions(+)
```

`git log` shows the full records. `--oneline` shows one line per commit: short hash, then the first line of the message. `git show HEAD` shows one commit: its message and its diff. The `--stat` option summarises changed files.

### 3.4 Looking at changes: `git diff`

`git diff` compares two of the three places. It is the most-used reading command, so learn exactly what it compares:

| Command | Compares |
|---|---|
| `git diff` | working tree **vs** index (changes not yet staged) |
| `git diff --staged` | index **vs** last commit (what the next commit will contain) |
| `git diff HEAD` | working tree vs last commit (everything) |
| `git diff a b` | commit `a` vs commit `b` |

Let us change the file, stage it, and change it again, so that all three places differ:

```text
$ echo '' >> price.py
$ echo '' >> price.py
$ echo 'def discount(price, percent):' >> price.py
$ echo '    return round(price * (1 - percent / 100), 2)' >> price.py
$ git add price.py
$ echo '' >> price.py
$ echo '# TODO: validate negative prices' >> price.py
$ git status --short
MM price.py
$ git diff
diff --git a/price.py b/price.py
index 1cb447a..ccdf7ff 100644
--- a/price.py
+++ b/price.py
@@ -9,3 +9,5 @@ def with_tax(price):

 def discount(price, percent):
     return round(price * (1 - percent / 100), 2)
+
+# TODO: validate negative prices
$ git diff --staged
diff --git a/price.py b/price.py
index dfe05e4..1cb447a 100644
--- a/price.py
+++ b/price.py
@@ -5,3 +5,7 @@ TAX_RATE = 0.18

 def with_tax(price):
     return round(price * (1 + TAX_RATE), 2)
+
+
+def discount(price, percent):
+    return round(price * (1 - percent / 100), 2)
```

`git status --short` shows two letters per file. The left letter is the **index** state, the right letter is the **working tree** state. `MM` means "modified in both": a staged change and a further unstaged change. `git diff` shows only the unstaged TODO line. `git diff --staged` shows only the staged `discount` function. Commit only the staged part:

```text
$ git commit -m "Add discount helper"
[main 47562ec] Add discount helper
 1 file changed, 4 insertions(+)
$ git status --short
 M price.py
```

The TODO line is still modified in the working tree and is **not** part of the commit. This is the staging area doing its job.

### 3.5 Putting a file back: `git restore`

To throw away an **unstaged** change in a file (careful: this cannot be undone, because git never saw that change):

```text
$ git restore price.py
$ git status
On branch main
nothing to commit, working tree clean
$ tail -n 3 price.py

def discount(price, percent):
    return round(price * (1 - percent / 100), 2)
```

And to un-stage something you added by mistake (the change stays in your working tree):

```text
$ echo '# note' >> price.py
$ git add price.py
$ git restore --staged price.py
$ git status --short
 M price.py
$ git restore price.py
```

`restore` without `--staged` touches the working tree. `restore --staged` touches only the index. That is the whole story.

### 3.6 Try it

**Predict the output.** You have a clean repository. You run:

```text
echo "x = 1" > a.py
git add a.py
echo "x = 2" > a.py
git status --short
```

What two characters does git print before `a.py`? Why? Then say what `git diff` and `git diff --staged` would show.

<details><summary>Answer</summary>

```text
$ cd ~/work
$ git init -q t
$ cd t
$ echo "x = 1" > a.py
$ git add a.py
$ echo "x = 2" > a.py
$ git status --short
AM a.py
$ git diff
diff --git a/a.py b/a.py
index 7d4290a..407de30 100644
--- a/a.py
+++ b/a.py
@@ -1 +1 @@
-x = 1
+x = 2
$ git diff --staged
diff --git a/a.py b/a.py
new file mode 100644
index 0000000..7d4290a
--- /dev/null
+++ b/a.py
@@ -0,0 +1 @@
+x = 1
```

`AM`: **A** in the left column (the file is *added* to the index) and **M** in the right column (the working tree copy is *modified* after staging). `git diff` shows `x = 1` replaced by `x = 2`, because it compares the index (with `1`) to the working tree (with `2`). `git diff --staged` shows the whole new file with `x = 1`, because it compares the last commit (nothing) to the index.

</details>

**Try it.** In an empty practice folder, make a repository with two files, `a.txt` and `b.txt`. Edit both. Stage and commit only `a.txt`. Use `git log --oneline` and `git status --short` to prove that `b.txt` is still modified and uncommitted.

## 4. Good commits, messages and `.gitignore`

### 4.1 What is a good commit?

A commit is a unit of communication. The best commits are:

- **Small and focused**: one logical change. "Add discount helper" is good. "Misc fixes" is bad.
- **Complete**: the code works (tests pass) after the commit, not only after the next one.
- **Explained**: the message tells the reader what and **why**.

Why small? Because small commits are easy to **review** (a reviewer can read ten lines), easy to **undo** (`git revert` one commit without losing other work), easy to **find bugs with** (`git bisect` can pinpoint the exact commit that broke something) and easy to **move** (`cherry-pick`). A 2,000-line commit can do none of those.

A useful test: can you describe the commit in one sentence without using the word "and"? If not, it is probably two commits.

### 4.2 The commit message

A widely used format:

```text
Short summary in the imperative mood (50 characters or less)

Longer explanation, if needed, wrapped at about 72 characters.
Say WHY the change was made, not only what changed (the diff
already shows what). Mention side effects and alternatives.

Fixes #42
```

Rules that matter:

- **First line**: a summary, at most about 50 characters, no full stop at the end.
- **Imperative mood**: "Add", "Fix", "Remove", as if giving an order to the code. Think: "If applied, this commit will *Add discount helper*." Not "Added" or "Adding".
- **Blank line** after the summary. Tools treat the first line as the title.
- **Body** (optional): explain *why*. The diff already shows what.

Compare:

| Bad | Good |
|---|---|
| `fix` | `Fix crash when cart is empty` |
| `changes` | `Round totals to two decimals` |
| `Updated stuff and also fixed the thing` | two separate commits |
| `asdf` | (never) |

Some teams use **Conventional Commits**: a prefix such as `feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:` followed by the summary (`fix: handle empty cart`). It is useful because tools can build a changelog automatically (section 15). Follow whatever your team uses. If you work alone, pick one style and keep it.

To write a message with a body from the command line, give `-m` twice (each `-m` is a paragraph):

```text
$ cd ~/work/shop
$ git commit --allow-empty -m "Round totals to two decimals" -m "Floating point sums such as 0.1 + 0.2 printed as 0.30000000000000004. Round once, at the end, so intermediate values keep their precision."
[main 9dd86b0] Round totals to two decimals
$ git log -1
commit 9dd86b0e4b39e302e7db0040436c27012b9bfeef
Author: Ada Learner <ada@example.com>
Date:   Fri Jan 2 15:00:00 2026 +0000

    Round totals to two decimals

    Floating point sums such as 0.1 + 0.2 printed as 0.30000000000000004. Round once, at the end, so intermediate values keep their precision.
```

(We used `--allow-empty` only so that this demo needs no file change. Normally a commit has changes.) Without `-m`, git opens your editor, which is the better way to write a long message.

### 4.3 `.gitignore`: files git must not track

Some files should never be in the repository:

- generated files: `__pycache__/`, `*.pyc`, `build/`, `dist/`, `*.egg-info/`
- the virtual environment: `.venv/`
- tool caches: `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`
- editor and operating system files: `.vscode/`, `.idea/`, `.DS_Store`
- **secrets**: `.env`, API keys, passwords, private keys

List patterns in a file called `.gitignore` at the top of the project:

```text
# Python
__pycache__/
*.py[cod]
*.egg-info/
build/
dist/

# Environments and secrets
.venv/
.env

# Tool caches
.pytest_cache/
.mypy_cache/
.ruff_cache/

# Editors and OS
.vscode/
.idea/
.DS_Store
```

Test it. Create some junk and a secret and see what git says:

```text
$ mkdir -p __pycache__ .venv
$ echo "junk" > __pycache__/price.cpython-314.pyc
$ echo "API_KEY=abc123" > .env
$ git status --short
?? .gitignore
$ git add .gitignore
$ git commit -m "Add .gitignore"
[main 537794f] Add .gitignore
 1 file changed, 20 insertions(+)
 create mode 100644 .gitignore
$ git status --short
$ git check-ignore -v .env
.gitignore:10:.env	.env
```

Before the `.gitignore` was committed, the junk showed as untracked (`??`). Once it exists, `__pycache__/`, `.venv/` and `.env` vanish from `status`. `git check-ignore -v` tells you **which rule** ignores a file, the quickest way to debug "why is git ignoring my file?" (or the reverse).

Pattern rules in one table:

| Pattern | Meaning |
|---|---|
| `*.pyc` | any file ending in `.pyc`, in any folder |
| `build/` | a folder named `build` (the slash means folder) |
| `/todo.txt` | only `todo.txt` at the top, not in sub-folders |
| `!keep.log` | an exception: do not ignore this file |
| `# text` | a comment |

> **Trap: `.gitignore` does not un-track.** If a file is *already committed*, adding it to `.gitignore` does nothing. You must run `git rm --cached file` (remove from the index, keep on disk) and commit. And if a **secret** was ever committed, ignoring it is not enough: the secret is in the history forever. You must **change the secret** (revoke the key), then, if needed, rewrite history. Treat every committed secret as public.

### 4.4 Try it

**Predict.** A teammate committed `config.local` by mistake last week. You add `config.local` to `.gitignore`. Next day `git status` still reports changes to `config.local`. Why, and what two commands fix it?

<details><summary>Answer</summary>

Because git already **tracks** the file, and `.gitignore` only affects *untracked* files. Fix:

```text
git rm --cached config.local
git commit -m "Stop tracking config.local"
```

The first command removes it from the index only (the file stays on disk). After the commit it is untracked, and now `.gitignore` applies.

</details>

## 5. Branches and merging

### 5.1 Why branches

Imagine you are adding a feature that takes three days. On day two your friend finds a bug in the released version and needs a fix **now**. If you work directly on the one line of history, your half-finished feature is mixed with the fix. With branches, the feature lives on its own line. The released line stays clean. When the feature is done, you **merge** it in.

Branches are cheap (a sticky note, remember), so the habit is: **one branch per task**. Name them for the task: `add-discount`, `fix-empty-cart`, `docs-readme`.

### 5.2 A tiny helper for the demos

Many demos below need "a commit with a file in it". To keep the commands short we use a two-line script called `mk`. It creates `NAME.txt` and commits it with the message `Add NAME`. You do not need it in real work. Put it in a folder that is on your `PATH`, or just type the three commands it contains.

```text
#!/bin/sh
# usage: mk NAME   (creates NAME.txt and commits it as "Add NAME")
echo "$1" > "$1.txt"
git add "$1.txt"
git commit -q -m "Add $1"
```

### 5.3 Creating and switching

```text
$ cd ~/work
$ mkdir tree
$ cd tree
$ git init -q
$ mk A
$ mk B
$ git branch
* main
$ git switch -c feature
Switched to a new branch 'feature'
$ git branch
* feature
  main
```

`git switch -c feature` means "create a branch called `feature` and move `HEAD` onto it". The star in `git branch` marks the current branch. (Older books use `git checkout -b feature`; it does the same. `switch` and `restore` were added to split the many jobs of `checkout` into clearer commands.)

Now commit twice on `feature`, then look at the graph with our `git lg` alias:

```text
$ mk C
$ mk D
$ git lg
* de653c3 (HEAD -> feature) Add D
* f6d38b0 Add C
* c66826d (main) Add B
* 2ee9eba Add A
```

Read `git lg` from top (newest) to bottom. `HEAD -> feature` says: `HEAD` points to the branch `feature`, which points at the newest commit. `main` is two commits behind. As a picture:

```text
A <-- B <-- C <-- D     <-- feature   (HEAD)
       ^
       main
```

Switch back to `main` and look at the files:

```text
$ git switch main
Switched to branch 'main'
$ ls
A.txt
B.txt
$ git switch feature
Switched to branch 'feature'
$ ls
A.txt
B.txt
C.txt
D.txt
```

Git rewrote your working tree: `C.txt` and `D.txt` appear and disappear as you move between branches. The files are not deleted. They are in the commits, and git re-creates the right state for the commit that `HEAD` points to.

> Git refuses to switch if you have uncommitted changes that would be overwritten. Commit them, or `stash` them (section 8).

### 5.4 Merging: the fast-forward case

Merge `feature` into `main`. Since `main` has not moved since `feature` was created, git does not need to create anything new. It just moves the `main` sticky note forward. This is a **fast-forward**:

```text
$ git switch main
Switched to branch 'main'
$ git merge feature
Updating c66826d..de653c3
Fast-forward
 C.txt | 1 +
 D.txt | 1 +
 2 files changed, 2 insertions(+)
 create mode 100644 C.txt
 create mode 100644 D.txt
$ git lg
* de653c3 (HEAD -> main, feature) Add D
* f6d38b0 Add C
* c66826d Add B
* 2ee9eba Add A
```

```text
before:   A <-- B <-- C <-- D   <-- feature
                 ^
                 main

after:    A <-- B <-- C <-- D   <-- feature, main
```

Remember the rule: **you merge INTO the branch you are standing on.** `git merge feature` brings `feature` into the current branch. Always check where you are first (`git branch` or `git status`).

### 5.5 Merging: when both lines moved

Now the interesting case. Two lines of history have each moved on:

```text
$ git switch -c docs
Switched to a new branch 'docs'
$ mk E
$ git switch main
Switched to branch 'main'
$ mk F
$ git lg
* a9d3e0b (HEAD -> main) Add F
| * c302d96 (docs) Add E
|/
* de653c3 (feature) Add D
* f6d38b0 Add C
* c66826d Add B
* 2ee9eba Add A
```

```text
        E        <-- docs
       /
A -- B -- C -- D -- F   <-- main   (HEAD)
```

(Our `lg` shows the same graph rotated. Read the `*` and `|` lines.) A fast-forward is impossible: `main` has `F`, `docs` has `E`, and neither contains the other. Git therefore makes a **merge commit** with two parents:

```text
$ git merge docs -m "Merge branch 'docs'"
Merge made by the 'ort' strategy.
 E.txt | 1 +
 1 file changed, 1 insertion(+)
 create mode 100644 E.txt
$ git lg
*   ece7e6c (HEAD -> main) Merge branch 'docs'
|\
| * c302d96 (docs) Add E
* | a9d3e0b Add F
|/
* de653c3 (feature) Add D
* f6d38b0 Add C
* c66826d Add B
* 2ee9eba Add A
$ git log --oneline --merges
ece7e6c Merge branch 'docs'
```

```text
A -- B -- C -- D -- F -- M    <-- main
                \       /
                 E ----
```

How did git know what to combine? It finds the **merge base**, the latest commit that both lines share (here `D`, where `docs` was created), and compares: what changed from the base to each tip? It applies both sets of changes. This is a **three-way merge**. Two inputs would not be enough, because with only two versions you cannot tell who changed what. If both sides changed the **same lines** differently, git cannot decide and stops with a **conflict**. That is the next section.

You can ask git for the merge base yourself:

```text
$ git merge-base main docs
c302d96b10575b9b14ea1c2247a9e693de518828
$ git rev-parse --short HEAD~1
a9d3e0b
```

### 5.6 Forcing a merge commit: `--no-ff`

A fast-forward leaves no trace that a branch existed. Some teams prefer to always record a merge commit so that the feature is visible as a unit:

```text
$ git switch -c extra
Switched to a new branch 'extra'
$ mk G
$ git switch main
Switched to branch 'main'
$ git merge --no-ff extra -m "Merge branch 'extra'"
Merge made by the 'ort' strategy.
 G.txt | 1 +
 1 file changed, 1 insertion(+)
 create mode 100644 G.txt
$ git lg
*   0ed7efb (HEAD -> main) Merge branch 'extra'
|\
| * 3810b26 (extra) Add G
|/
*   ece7e6c Merge branch 'docs'
|\
| * c302d96 (docs) Add E
* | a9d3e0b Add F
|/
* de653c3 (feature) Add D
* f6d38b0 Add C
* c66826d Add B
* 2ee9eba Add A
```

`--no-ff` ("no fast-forward") creates the merge commit even when a fast-forward would do. Whether to prefer a merge commit, a fast-forward, or a squash is a **team policy**, and we discuss the options in section 10.

### 5.7 Deleting branches

After a branch is merged, its sticky note is no longer needed. The commits stay in the history.

```text
$ git branch --merged
  docs
  extra
  feature
* main
$ git branch -d docs extra feature
Deleted branch docs (was c302d96).
Deleted branch extra (was 3810b26).
Deleted branch feature (was de653c3).
$ git branch
* main
```

`-d` (small d) is safe: git refuses to delete a branch whose commits are **not merged** anywhere, because those commits would become unreachable. `-D` (capital) forces the deletion. Use capital D only when you really want to throw the work away.

### 5.8 Try it

**Predict.** `main` and `fix` both start from commit `B`. `fix` has one new commit `X`; `main` has none. You are on `main` and run `git merge fix`. Is a merge commit created? What does `git lg` show afterwards?

<details><summary>Answer</summary>

```text
$ cd ~/work
$ mkdir ff
$ cd ff
$ git init -q
$ mk A
$ mk B
$ git switch -q -c fix
$ mk X
$ git switch -q main
$ git merge fix
Updating 6bef0ae..fc82dc8
Fast-forward
 X.txt | 1 +
 1 file changed, 1 insertion(+)
 create mode 100644 X.txt
$ git lg
* fc82dc8 (HEAD -> main, fix) Add X
* 6bef0ae Add B
* 064ca01 Add A
```

No merge commit: `main` is a direct ancestor of `fix`, so git does a fast-forward. Both names point at `X` and the history is a straight line.

</details>

**Try it.** Build the diverged situation of 5.5 in your own practice folder. After the merge, run `git log --oneline --graph` and `git log --first-parent --oneline`. What does `--first-parent` hide, and why might a team find it useful?

## 6. Merge conflicts

### 6.1 What a conflict is, and why it is not scary

A conflict is git saying: "Both of you changed the same lines, and I cannot guess which version you want. Please decide." That is all. It is a normal part of teamwork. Git never loses either version: both are put in the file for you to choose from. You are always one command (`git merge --abort`) away from the state before the merge started.

Conflicts become less scary when you know the three rules:

1. Conflicts happen only when the **same region** was changed on both sides (or one side deleted what the other edited).
2. Git marks the conflicting region in the file with special lines. You edit the file to the final text.
3. You tell git "done" with `git add`, then finish with `git commit`.

### 6.2 Setting up a real conflict

We use a small price list. Both branches change the price of `tea`.

```text
$ cd ~/work
$ mkdir cafe
$ cd cafe
$ git init -q
```

```python
PRICES = {
    "tea": 20,
    "coffee": 30,
    "cake": 50,
}
```

```text
$ git add menu.py
$ git commit -q -m "Add price list"
$ git switch -q -c feature
```

On the `feature` branch, the cafe raises the price of tea and adds juice:

```python
PRICES = {
    "tea": 25,
    "coffee": 30,
    "cake": 50,
    "juice": 40,
}
```

```text
$ git commit -q -am "Raise tea price, add juice"
$ git switch -q main
```

Meanwhile on `main`, someone else cuts the price of tea:

```python
PRICES = {
    "tea": 15,
    "coffee": 30,
    "cake": 50,
}
```

```text
$ git commit -q -am "Cut tea price for the winter sale"
$ git lg
* 08cab30 (HEAD -> main) Cut tea price for the winter sale
| * b96bc5a (feature) Raise tea price, add juice
|/
* d34e1d4 Add price list
```

### 6.3 The merge stops

```text
$ git merge feature
Auto-merging menu.py
CONFLICT (content): Merge conflict in menu.py
Automatic merge failed; fix conflicts and then commit the result.
$ git status
On branch main
You have unmerged paths.
  (fix conflicts and run "git commit")
  (use "git merge --abort" to abort the merge)

Unmerged paths:
  (use "git add <file>..." to mark resolution)
	both modified:   menu.py

no changes added to commit (use "git add" and/or "git commit -a")
```

Read this carefully. The `merge` command says `CONFLICT (content)`: the merge is **unfinished**. `git status` lists the file under "Unmerged paths: both modified". The repository is in a special "merging" state. The `juice` change merged cleanly; only the tea line is a problem. Look at the file:

```text
$ cat menu.py
PRICES = {
<<<<<<< HEAD
    "tea": 15,
=======
    "tea": 25,
>>>>>>> feature
    "coffee": 30,
    "cake": 50,
    "juice": 40,
}
```

Git wrote **conflict markers** around the disputed lines:

| Marker | Meaning |
|---|---|
| `<<<<<<< HEAD` | start of **your** side (the branch you are on, `main`) |
| `=======` | divider |
| `>>>>>>> feature` | end of **their** side (the branch being merged) |

Everything outside the markers is merged already. Inside, you see both versions. The `juice` line has no markers because it did not conflict.

### 6.4 Resolving

Resolving means: edit the file until it contains exactly what you want, with **all marker lines removed**. You have three choices: keep yours, keep theirs, or write something new. Here the shop owner decides the winter sale price (15) should win, but keep `juice`. Write the final file:

```python
PRICES = {
    "tea": 15,
    "coffee": 30,
    "cake": 50,
    "juice": 40,
}
```

Tell git the file is resolved with `git add`, check, then commit:

```text
$ git add menu.py
$ git status
On branch main
All conflicts fixed but you are still merging.
  (use "git commit" to conclude merge)

Changes to be committed:
	modified:   menu.py
$ git commit
[main 11900f8] Merge branch 'feature'
$ git lg
*   11900f8 (HEAD -> main) Merge branch 'feature'
|\
| * b96bc5a (feature) Raise tea price, add juice
* | 08cab30 Cut tea price for the winter sale
|/
* d34e1d4 Add price list
```

`git commit` with no `-m` normally opens your editor with a ready-made message ("Merge branch 'feature'"). On the test machine the editor was set to accept the message as it is. The result is a merge commit with two parents. The history records that two lines were joined and how.

Before committing, verify that no marker survived anywhere. This command finds leftovers (it prints nothing when clean):

```text
$ git grep -n -e '<<<<<<<' -e '>>>>>>>' || echo "no markers left"
no markers left
$ python -c "import menu; print(menu.PRICES)"
{'tea': 15, 'coffee': 30, 'cake': 50, 'juice': 40}
```

> **Always run the tests after resolving.** A conflict fix can be syntactically fine and logically wrong. Two changes that were each correct alone may break each other. The merge commit deserves the same care as any other commit.

### 6.5 Shortcuts, and giving up

You do not always need to edit by hand:

- `git checkout --ours file` or `git restore --ours file`: take **your** version of the whole file (the branch you are on).
- `git checkout --theirs file`: take the other branch's version of the whole file.
- `git merge --abort`: forget the whole merge, return to how things were before `git merge`.
- `git mergetool`: open a graphical three-way editor (VS Code, meld, ...). VS Code shows "Accept Current / Accept Incoming / Accept Both" buttons above each conflict. They only insert the text for you; you still decide.

Let us practise giving up. We rewind `main` by one commit (undoing the merge), start the same merge again, and abort:

```text
$ git reset -q --hard HEAD^
$ git merge feature
Auto-merging menu.py
CONFLICT (content): Merge conflict in menu.py
Automatic merge failed; fix conflicts and then commit the result.
$ git merge --abort
$ git status
On branch main
nothing to commit, working tree clean
```

(The `reset --hard HEAD^` step moved `main` back to its first parent, before the merge, so that the conflict happens again. We explain `reset` in section 9.) After `--abort`, the working tree is clean and there is no half-merge. It is as if you never ran the command.

### 6.6 How to avoid conflicts

You cannot avoid all of them, but you can make them rare and small:

- **Pull often.** Bring in other people's work every day, so you never face a 3-week-old divergence.
- **Keep branches short-lived** (days, not months).
- **Make small commits and small pull requests.**
- **Do not reformat whole files** in a feature commit. A formatting change touches every line and conflicts with everything. Do formatting in its own commit, ideally agreed with the team.
- **Talk.** If two people must edit the same function, tell each other.

### 6.7 Try it

**Predict.** On `main` you changed line 2 of a file. On `feature` a teammate changed line 20 of the same file. Is there a conflict?

<details><summary>Answer</summary>

No. The changes are in different regions, far apart. Git applies both changes automatically. Conflicts need the **same lines** (or touching neighbours) edited on both sides.

</details>

**Try it.** Recreate the cafe conflict. This time resolve it by choosing `--theirs` for the whole file (`git checkout --theirs menu.py`). Which tea price do you get? Which lines did you lose from `main`?

## 7. Rebase and interactive rebase

### 7.1 The idea: replay your commits

Merge joins two lines and records the join. **Rebase** does something different: it takes your commits and **replays them on top of a new base**, as if you had started your work later. The result is a straight line.

Start with this situation:

```text
          D -- E        <-- feature
         /
A -- B -- C             <-- main
```

`feature` started from `B`, but `main` has since moved to `C`. Now (standing on `feature`) run `git rebase main`. Git finds `D` and `E`, sets them aside, moves to `C`, and re-applies each one:

```text
                   D' -- E'     <-- feature
                  /
A -- B -- C -------             <-- main
```

`D'` and `E'` are **new commits** with the same changes and messages but different parents, so they have **different hashes**. The old `D` and `E` still exist for a while but nothing points to them. Let us do it for real:

```text
$ cd ~/work
$ mkdir rb
$ cd rb
$ git init -q
$ mk A
$ mk B
$ git switch -q -c feature
$ mk D
$ mk E
$ git switch -q main
$ mk C
$ git lg
* f6869a5 (HEAD -> main) Add C
| * d3bb731 (feature) Add E
| * 367d62e Add D
|/
* f8eedce Add B
* 28587d1 Add A
```

Now rebase `feature` onto `main`:

```text
$ git switch -q feature
$ git rebase main
Rebasing (1/2)
Rebasing (2/2)
Successfully rebased and updated refs/heads/feature.
$ git lg
* a0d179d (HEAD -> feature) Add E
* b2f08c9 Add D
* f6869a5 (main) Add C
* f8eedce Add B
* 28587d1 Add A
```

`D` and `E` now sit after `C`, with new hashes (compare with the graph above: the letters after `Add D` and `Add E` changed). The history is a straight line; there is no merge commit. Finally, `main` can simply fast-forward:

```text
$ git switch -q main
$ git merge --ff-only feature
Updating f6869a5..a0d179d
Fast-forward
 D.txt | 1 +
 E.txt | 1 +
 2 files changed, 2 insertions(+)
 create mode 100644 D.txt
 create mode 100644 E.txt
$ git lg
* a0d179d (HEAD -> main, feature) Add E
* b2f08c9 Add D
* f6869a5 Add C
* f8eedce Add B
* 28587d1 Add A
```

`--ff-only` says "only merge if it is a pure fast-forward, otherwise fail". It is a safe habit: it refuses to create surprise merge commits.

### 7.2 Merge or rebase?

| | Merge | Rebase |
|---|---|---|
| History shape | true graph, shows when lines joined | straight line |
| Changes commits? | no, existing commits stay | yes, makes new commits (new hashes) |
| Conflicts | resolve once | may resolve once per replayed commit |
| Risk | low | higher if used on shared history |
| Good for | joining finished work into `main` | tidying **your own** local work before sharing |

Neither is "right". Many teams use both: rebase your feature branch on `main` to stay up to date and keep it tidy, then merge (or squash-merge) it into `main`.

### 7.3 The golden rule of rebase

> **Never rebase commits that other people already have.**

Why? Rebase makes new commits and abandons the old ones. If a teammate has the old `D` and `E`, her history now contains commits that yours does not. When you push your rewritten branch (you must force it) and she pulls, git sees two versions of the same work and tries to merge them, giving duplicate commits and confusing conflicts. Everyone loses time.

So the rule of thumb:

- Commits **only on your machine** (not pushed): rewrite freely.
- Commits **already pushed to a shared branch** such as `main`: do not rewrite.
- Your own pushed feature branch that nobody else uses: rewriting is acceptable, but you will need `git push --force-with-lease` (section 10).

### 7.4 Conflicts during a rebase

Rebase replays commits one at a time, so a conflict can appear in the middle. The commands are:

| Command | Meaning |
|---|---|
| (fix the file, then) `git add file` | mark the conflict as resolved |
| `git rebase --continue` | go on with the next commit |
| `git rebase --skip` | drop the commit that is conflicting |
| `git rebase --abort` | stop and return to how it was before |

A detail that confuses everyone: **during a rebase, "ours" and "theirs" are swapped.** "Ours" (`HEAD`) is the branch you are rebasing *onto* (the new base), and "theirs" is **your own commit** being replayed. Do not memorise it; read the markers: git writes the branch or commit name beside each marker.

### 7.5 Interactive rebase: rewrite your own history

`git rebase -i` ("interactive") opens an editor with a **to-do list**, one line per commit, oldest first. You edit the list; git then follows your instructions. Let us see the list git offers. We make four messy commits first:

```text
$ cd ~/work
$ mkdir messy
$ cd messy
$ git init -q
$ mk base
$ mk login
$ mk typo
$ mk oops
$ git log --oneline
7a28e21 Add oops
7adf34a Add typo
f39db31 Add login
a802d5f Add base
```

Normally `git rebase -i HEAD~3` opens an editor on the list. The environment variable `GIT_SEQUENCE_EDITOR` lets us name a *different* program to act as the editor, which is how we can show the list here without a human. Using `cat` as the "editor" prints the list and changes nothing:

```text
$ GIT_SEQUENCE_EDITOR=cat git rebase -i HEAD~3
pick f39db31 # Add login
pick 7adf34a # Add typo
pick 7a28e21 # Add oops

# Rebase a802d5f..7a28e21 onto a802d5f (3 commands)
#
# Commands:
# p, pick <commit> = use commit
# r, reword <commit> = use commit, but edit the commit message
# e, edit <commit> = use commit, but stop for amending
# s, squash <commit> = use commit, but meld into previous commit
# f, fixup [-C | -c] <commit> = like "squash" but keep only the previous
#                    commit's log message, unless -C is used, in which case
#                    keep only this commit's message; -c is same as -C but
#                    opens the editor
# x, exec <command> = run command (the rest of the line) using shell
# b, break = stop here (continue rebase later with 'git rebase --continue')
# d, drop <commit> = remove commit
# l, label <label> = label current HEAD with a name
# t, reset <label> = reset HEAD to a label
# m, merge [-C <commit> | -c <commit>] <label> [# <oneline>]
#         create a merge commit using the original merge commit's
#         message (or the oneline, if no original merge commit was
#         specified); use -c <commit> to reword the commit message
# u, update-ref <ref> = track a placeholder for the <ref> to be updated
#                       to this position in the new commits. The <ref> is
#                       updated at the end of the rebase
#
# These lines can be re-ordered; they are executed from top to bottom.
#
# If you remove a line here THAT COMMIT WILL BE LOST.
#
# However, if you remove everything, the rebase will be aborted.
#
Successfully rebased and updated refs/heads/main.
$ git log --oneline
7a28e21 Add oops
7adf34a Add typo
f39db31 Add login
a802d5f Add base
```

Study the to-do list. Each line is `command hash message`. The comments (lines starting with `#`) are git's built-in help. The commands you will use:

| Command | Short | What it does |
|---|---|---|
| `pick` | `p` | keep the commit as it is |
| `reword` | `r` | keep the changes, edit the message |
| `edit` | `e` | stop after this commit so you can change it (amend, split) |
| `squash` | `s` | merge into the previous commit, combine messages |
| `fixup` | `f` | merge into the previous commit, discard this message |
| `drop` | `d` | delete the commit |

You can also **reorder** by moving lines. The to-do is processed from top to bottom.

Now a real use. The commits `typo` and `oops` are noise: they just fix `login`. We want one clean commit "Add login". In your editor you would change the word `pick` to `fixup` on the last two lines. Here we do the same edit with `sed`:

```text
$ GIT_SEQUENCE_EDITOR="sed -i -e '2,3s/^pick/fixup/'" git rebase -i HEAD~3
Rebasing (2/3)
Rebasing (3/3)
Successfully rebased and updated refs/heads/main.
$ git log --oneline
99eea39 Add login
a802d5f Add base
```

Three commits became one: `login`, with the changes of `typo` and `oops` folded into it. The files are all still there:

```text
$ ls
base.txt
login.txt
oops.txt
typo.txt
```

On your own machine you would just open the editor, change the words by hand, and save. `GIT_SEQUENCE_EDITOR` is only how this book demonstrates it without a human. (`sed -i` works the same in Git Bash on Windows.)

### 7.6 `reword` and `squash`

`reword` stops to let you edit a message. `squash` combines commits and *also* lets you edit the combined message, and is the usual tool before opening a pull request ("clean up my 8 work-in-progress commits into 2 good ones"). Here is a squash. We set `core.editor` to `true` (a program that does nothing and succeeds), so git accepts the proposed combined message unchanged:

```text
$ mk search
$ mk search-fix
$ mk search-docs
$ GIT_SEQUENCE_EDITOR="sed -i -e '2,3s/^pick/squash/'" git rebase -i HEAD~3
Rebasing (2/3)
Rebasing (3/3)
[detached HEAD 3286c25] Add search
 Date: Wed Jan 7 00:00:00 2026 +0000
 3 files changed, 3 insertions(+)
 create mode 100644 search-docs.txt
 create mode 100644 search-fix.txt
 create mode 100644 search.txt
Successfully rebased and updated refs/heads/main.
$ git log --oneline
3286c25 Add search
99eea39 Add login
a802d5f Add base
$ git log -1 --format=%B
Add search

Add search-fix

Add search-docs
```

The new message is the three original messages joined. In a real session your editor opens on that text and you tidy it into one good message.

### 7.7 `commit --fixup` and `--autosquash`

A very practical pattern: you notice a problem in an **older** commit of your branch. Instead of editing the history by hand, make a "fixup commit" now and let git put it in the right place later:

```text
$ mk feature1
$ mk feature2
$ echo "fixed" > feature1.txt
$ git add feature1.txt
$ git commit -q --fixup HEAD~1
$ git log --oneline
a076a69 fixup! Add feature1
924c6c4 Add feature2
86ff460 Add feature1
3286c25 Add search
99eea39 Add login
a802d5f Add base
$ GIT_SEQUENCE_EDITOR=true git rebase -i --autosquash HEAD~3
Rebasing (2/3)
Rebasing (3/3)
Successfully rebased and updated refs/heads/main.
$ git log --oneline
1b6abc1 Add feature2
e39a252 Add feature1
3286c25 Add search
99eea39 Add login
a802d5f Add base
$ cat feature1.txt
fixed
```

`git commit --fixup <commit>` creates a commit named `fixup! Add feature1`. `--autosquash` reorders the to-do list so that it sits right after its target and turns it into `fixup`. (`GIT_SEQUENCE_EDITOR=true` accepts the generated list without opening anything.) The fix is now part of the original commit as if it had always been right.

### 7.8 Edit the last commit: `--amend`

For just the **last** commit you do not need rebase:

```text
$ mk widget
$ echo "widget v2" > widget.txt
$ git add widget.txt
$ git commit --amend -m "Add widget (version 2)"
[main 0fd2e7d] Add widget (version 2)
 Date: Wed Jan 7 15:00:00 2026 +0000
 1 file changed, 1 insertion(+)
 create mode 100644 widget.txt
$ git log --oneline -3
0fd2e7d Add widget (version 2)
1b6abc1 Add feature2
e39a252 Add feature1
```

`--amend` replaces the last commit with a new one (new hash!) containing the staged changes and the new message. Same golden rule: do not amend a commit you already pushed to a shared branch.

### 7.9 Try it

**Predict.** After `git rebase main` on `feature`, `git lg` shows `D` and `E` with different hashes than before. A colleague had already pulled the old `D` and `E`. What does she see when she next pulls your force-pushed branch?

<details><summary>Answer</summary>

Her local branch contains the **old** `D` and `E`, while the remote now has `D'` and `E'`. Git sees two histories that share only `B` and treats them as diverged. A plain `git pull` tries to merge them, producing duplicates of the same changes and possibly conflicts. That is why the golden rule forbids rewriting shared commits. If it happens anyway she must run `git fetch` and `git reset --hard origin/feature` after saving any work of her own.

</details>

**Try it.** In a practice repository, make five commits named `one` to `five` (use `mk`). With an interactive rebase: reorder so `five` comes first, `drop` `three`, and `squash` `four` into `two`. Check the result with `git log --oneline` and confirm that `three.txt` is gone.

## 8. `cherry-pick` and `stash`

### 8.1 `cherry-pick`: copy one commit

Sometimes you want **one commit** from another branch, not the whole branch. A classic case: you fixed a bug while working on an experimental branch, and the fix is needed on `main` today. `git cherry-pick` takes one commit, calculates its change, and applies it on top of the current branch as a **new commit** (new hash, same message).

```text
$ cd ~/work
$ mkdir pick
$ cd pick
$ git init -q
$ mk A
$ mk B
$ git switch -q -c experiment
$ mk X
$ echo "rounding fixed" > hotfix.txt
$ git add hotfix.txt
$ git commit -q -m "Fix rounding bug"
$ mk Y
$ git lg
* 253b5f4 (HEAD -> experiment) Add Y
* a8138ca Fix rounding bug
* 1cb00e3 Add X
* c57b9c3 (main) Add B
* 3414e77 Add A
```

The fix is the commit in the middle of `experiment`. `experiment~1` means "one commit before the tip of `experiment`". Pick it onto `main`:

```text
$ git switch -q main
$ git cherry-pick -x experiment~1
[main 3431e21] Fix rounding bug
 Date: Thu Jan 8 04:00:00 2026 +0000
 1 file changed, 1 insertion(+)
 create mode 100644 hotfix.txt
$ git lg
* 3431e21 (HEAD -> main) Fix rounding bug
| * 253b5f4 (experiment) Add Y
| * a8138ca Fix rounding bug
| * 1cb00e3 Add X
|/
* c57b9c3 Add B
* 3414e77 Add A
```

`-x` appends a line "(cherry picked from commit ...)" to the message. That is a kindness to your future self: the link between the two copies is recorded. Notice that the original commit still exists on `experiment`, and the copy has a different hash.

Cherry-pick is a precision tool. Use it for hot fixes and for "rescue one commit out of a branch". Do **not** use it as your normal way of moving work around: if you copy commits and later merge the branch, git sees two copies of the change and the history becomes confusing. Conflicts can also occur during a cherry-pick; you resolve them exactly as in section 6, and then run `git cherry-pick --continue` (or `--abort`).

### 8.2 `stash`: a drawer for unfinished work

You are halfway through a change when you must switch branches (a bug report arrives). The work is not ready to commit. `git stash` puts your uncommitted changes in a drawer and gives you back a clean working tree:

```text
$ echo "work in progress" >> A.txt
$ echo "a note to self" > notes.txt
$ git status --short
 M A.txt
?? notes.txt
$ git stash
Saved working directory and index state WIP on main: 3431e21 Fix rounding bug
$ git status --short
?? notes.txt
$ git stash list
stash@{0}: WIP on main: 3431e21 Fix rounding bug
```

The tracked file `A.txt` was stashed. The untracked `notes.txt` was **left behind**: by default stash ignores new files. Add `-u` (`--include-untracked`) to take them too:

```text
$ git stash -u
Saved working directory and index state WIP on main: 3431e21 Fix rounding bug
$ git status --short
$ git stash list
stash@{0}: WIP on main: 3431e21 Fix rounding bug
stash@{1}: WIP on main: 3431e21 Fix rounding bug
```

You can now switch branches and fix things freely. When you come back, take the work out of the drawer:

```text
$ git stash pop
Already up to date.
On branch main
Untracked files:
  (use "git add <file>..." to include in what will be committed)
	notes.txt

nothing added to commit but untracked files present (use "git add" to track)
Dropped refs/stash@{0} (d539914e951fc7b376c7cd575a54e340d78059be)
$ git status --short
?? notes.txt
$ git stash pop
On branch main
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
	modified:   A.txt

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	notes.txt

no changes added to commit (use "git add" and/or "git commit -a")
Dropped refs/stash@{0} (5b98ed5c2d7d806a67a7ae41976fa3740e9061c3)
$ git status --short
 M A.txt
?? notes.txt
$ git stash list
```

| Command | What it does |
|---|---|
| `git stash` / `git stash push -m "msg"` | save tracked changes (message optional) |
| `git stash -u` | also save untracked files |
| `git stash list` | show the drawer (newest is `stash@{0}`) |
| `git stash pop` | re-apply the newest and remove it from the drawer |
| `git stash apply` | re-apply, but keep it in the drawer |
| `git stash drop` | throw away the newest |

The drawer is a stack: last in, first out. Do not use it as long-term storage. A stash has no branch and a vague name; after a few weeks nobody knows what `stash@{3}` was. If the work matters, commit it to a branch (`git switch -c wip-thing; git commit -am wip`). You can tidy that commit later with an interactive rebase.

### 8.3 Try it

**Predict.** You ran `git stash` and then `git stash pop` on a *different* branch where the same lines have changed. What will happen?

<details><summary>Answer</summary>

A stash is applied like a merge, so you may get a **conflict**, resolved exactly as in section 6. When `pop` conflicts, git keeps the stash in the drawer (so you do not lose it) and leaves conflict markers in your files. After you fix them, run `git add` on the files and `git stash drop` yourself.

</details>

## 9. Undoing mistakes safely

### 9.1 A decision table

Everyone makes mistakes with git. The skill is picking the right undo for the situation. The table below is the most useful page of this chapter; read it twice.

| Situation | Command | Safe? |
|---|---|---|
| Edited a file, want the last committed version back | `git restore file` | **No**: edits are lost for good |
| Staged the wrong file | `git restore --staged file` | yes |
| Last commit has a typo in the message, or a forgotten file (not pushed) | `git commit --amend` | yes if not pushed |
| Last few commits are wrong, **not pushed**, want to rework them | `git reset --soft` or `--mixed` | yes |
| Last few commits are wrong, **not pushed**, throw them away | `git reset --hard` | **No** (but `reflog` can save you) |
| Bad commit is **already pushed** and shared | `git revert <commit>` | yes: adds a new commit |
| Wrong branch, commit is somewhere else | `cherry-pick` + `reset` | yes |
| "I lost a commit!" | `git reflog` | yes |

The big idea: **if the commit is shared, never rewrite; add a new commit that undoes it (`revert`). If it is only yours, you may rewrite (`reset`, `amend`).**

### 9.2 `reset`: move the branch pointer

`git reset <commit>` moves the **current branch** to `<commit>`. It has three modes that decide what happens to the other two places (index, working tree):

| Mode | Branch moves | Index reset | Working tree reset |
|---|---|---|---|
| `--soft` | yes | no | no |
| `--mixed` (default) | yes | yes | no |
| `--hard` | yes | yes | **yes** |

So `--soft` is the gentlest (your changes stay staged), `--mixed` un-stages them (changes stay in files), and `--hard` throws everything away. Let us watch each one. First a repository with four commits:

```text
$ cd ~/work
$ mkdir undo
$ cd undo
$ git init -q
$ mk one
$ mk two
$ mk three
$ mk four
$ git log --oneline
9568c94 Add four
3650a03 Add three
f0b7bb3 Add two
bf14fa5 Add one
```

**Soft**: undo the last commit but keep its content staged. Good for "I committed too early, I want to add more to it":

```text
$ git reset --soft HEAD~1
$ git log --oneline
3650a03 Add three
f0b7bb3 Add two
bf14fa5 Add one
$ git status --short
A  four.txt
```

The commit `four` is gone from the log, but `four.txt` is staged (`A`), ready to be committed again. Commit it back, then try **mixed**:

```text
$ git commit -q -m "Add four"
$ git reset HEAD~1
$ git status --short
?? four.txt
$ git log --oneline
3650a03 Add three
f0b7bb3 Add two
bf14fa5 Add one
```

`four.txt` is still on disk but now untracked (`??`). The index forgot it. Mixed is good for "split this commit into smaller ones": un-commit, then `git add` the pieces separately. Last, **hard**:

```text
$ git add four.txt
$ git commit -q -m "Add four"
$ git reset --hard HEAD~2
HEAD is now at f0b7bb3 Add two
$ git log --oneline
f0b7bb3 Add two
bf14fa5 Add one
$ ls
one.txt
two.txt
```

Two commits and their files are gone from the branch **and** from the disk. That is why `--hard` is the dangerous one: it also throws away uncommitted changes in tracked files, and those can never be recovered. But the *commits* are not truly gone yet. See the next part.

### 9.3 `reflog`: the safety net under the safety net

Git keeps a private diary called the **reflog**: every position `HEAD` has been at, with a reason. Commits that no branch points to are not deleted for a long time (about 30 to 90 days by default), so the reflog can bring them back.

```text
$ git reflog
f0b7bb3 HEAD@{0}: reset: moving to HEAD~2
b29ed88 HEAD@{1}: commit: Add four
3650a03 HEAD@{2}: reset: moving to HEAD~1
25b416c HEAD@{3}: commit: Add four
3650a03 HEAD@{4}: reset: moving to HEAD~1
9568c94 HEAD@{5}: commit: Add four
3650a03 HEAD@{6}: commit: Add three
f0b7bb3 HEAD@{7}: commit: Add two
bf14fa5 HEAD@{8}: commit (initial): Add one
```

Read it newest-first: `HEAD@{0}` is where you are now; `HEAD@{1}` is where you were one move ago. Our `reset --hard` shows as the top line. The commit `Add four` is one line below. To undo the reset, move the branch back:

```text
$ git reset --hard 'HEAD@{1}'
HEAD is now at b29ed88 Add four
$ git log --oneline
b29ed88 Add four
3650a03 Add three
f0b7bb3 Add two
bf14fa5 Add one
$ ls
four.txt
one.txt
three.txt
two.txt
```

Everything is back. Remember this when panic strikes: **committed work is almost impossible to lose.** The reflog works only on your own machine, and only for things you committed (or stashed). Uncommitted edits destroyed by `reset --hard` or `restore` are gone.

**Rescuing a deleted branch.** Same tool. We create a branch with a commit, delete it with the capital `-D`, and bring it back:

```text
$ git switch -q -c work
$ mk work1
$ mk work2
$ git switch -q main
$ git branch -D work
Deleted branch work (was 8a943b9).
$ git reflog | head -5
b29ed88 HEAD@{0}: checkout: moving from work to main
8a943b9 HEAD@{1}: commit: Add work2
cfbc9bf HEAD@{2}: commit: Add work1
b29ed88 HEAD@{3}: checkout: moving from main to work
b29ed88 HEAD@{4}: reset: moving to HEAD@{1}
```

`git branch -D` itself printed the short hash of the old tip. The reflog also shows it. `HEAD@{1}` was the last place before we switched to `main`, which is the tip of `work`:

```text
$ git branch work-rescued 'HEAD@{1}'
$ git lg
* 8a943b9 (work-rescued) Add work2
* cfbc9bf Add work1
* b29ed88 (HEAD -> main) Add four
* 3650a03 Add three
* f0b7bb3 Add two
* bf14fa5 Add one
```

### 9.4 `revert`: undo by adding

If the bad commit was already pushed, other people have it. You cannot delete it from their copies. Instead you add **a new commit that does the exact opposite**:

```text
$ git switch -q main
$ mk mistake
$ git revert --no-edit HEAD
[main f0e4840] Revert "Add mistake"
 Date: Sat Jan 10 09:00:00 2026 +0000
 1 file changed, 1 deletion(-)
 delete mode 100644 mistake.txt
$ git log --oneline -3
f0e4840 Revert "Add mistake"
2140dc1 Add mistake
b29ed88 Add four
$ ls
four.txt
one.txt
three.txt
two.txt
```

`mistake.txt` was created by one commit and removed by another. The history stays honest: it shows the mistake and its correction. Reverting is always safe for shared history. It can be reverted again ("revert the revert") if you change your mind.

Reverting a **merge commit** needs one more word, because git must know which parent is "the mainline": `git revert -m 1 <merge-commit>` (keep parent number 1, which is the branch you merged *into*).

### 9.5 Detached HEAD, and getting out of it

If you check out a commit instead of a branch, you are in "detached HEAD" state:

```text
$ git switch --detach HEAD~3
HEAD is now at 3650a03 Add three
$ mk lost
$ git switch main
Warning: you are leaving 1 commit behind, not connected to
any of your branches:

  f218cd2 Add lost

If you want to keep it by creating a new branch, this may be a good time
to do so with:

 git branch <new-branch-name> f218cd2

Switched to branch 'main'
```

Git printed a long warning on the way out. It said: "you are leaving 1 commit behind, not connected to any of your branches". Read it; it tells you exactly how to save the commit (`git branch <name> <hash>`). If you ignore it, the commit is still in the reflog for a while:

```text
$ git reflog | head -3
f0e4840 HEAD@{0}: checkout: moving from f218cd2fa733fde7fefccbb4fd4feb7c644aa8d8 to main
f218cd2 HEAD@{1}: commit: Add lost
3650a03 HEAD@{2}: checkout: moving from main to HEAD~3
$ git branch rescue 'HEAD@{1}'
$ git lg
* f218cd2 (rescue) Add lost
| * f0e4840 (HEAD -> main) Revert "Add mistake"
| * 2140dc1 Add mistake
| | * 8a943b9 (work-rescued) Add work2
| | * cfbc9bf Add work1
| |/
| * b29ed88 Add four
|/
* 3650a03 Add three
* f0b7bb3 Add two
* bf14fa5 Add one
```

When is detached HEAD useful? For looking at an old version (`git switch --detach v1.0`) or running the tests at some commit. If you want to make changes, create a branch first (`git switch -c name`).

### 9.6 Cleaning untracked files

`git clean` deletes untracked files. It is destructive, so always do a **dry run** first:

```text
$ echo "junk" > scratch.tmp
$ git clean -n
Would remove scratch.tmp
$ git clean -f
Removing scratch.tmp
$ ls scratch.tmp
ls: cannot access 'scratch.tmp': No such file or directory
```

`-n` ("dry run") lists what would be removed. `-f` ("force") removes it. Add `-d` for untracked folders, `-x` to also remove ignored files (this deletes your `.venv`, so think twice).

### 9.7 Detective tools: find where a bug came from

History is not only a safety net, it is a search engine. Three tools save hours.

**`git blame`** shows who last changed each line, and in which commit:

```text
$ cd ~/work/shop
$ git blame price.py
^d45c12d (Ada Learner 2026-01-01 07:00:00 +0000  1) """Price helpers."""
^d45c12d (Ada Learner 2026-01-01 07:00:00 +0000  2)
^d45c12d (Ada Learner 2026-01-01 07:00:00 +0000  3) TAX_RATE = 0.18
^d45c12d (Ada Learner 2026-01-01 07:00:00 +0000  4)
^d45c12d (Ada Learner 2026-01-01 07:00:00 +0000  5)
^d45c12d (Ada Learner 2026-01-01 07:00:00 +0000  6) def with_tax(price):
^d45c12d (Ada Learner 2026-01-01 07:00:00 +0000  7)     return round(price * (1 + TAX_RATE), 2)
47562ec0 (Ada Learner 2026-01-01 22:00:00 +0000  8)
47562ec0 (Ada Learner 2026-01-01 22:00:00 +0000  9)
47562ec0 (Ada Learner 2026-01-01 22:00:00 +0000 10) def discount(price, percent):
47562ec0 (Ada Learner 2026-01-01 22:00:00 +0000 11)     return round(price * (1 - percent / 100), 2)
```

(The hashes, names and dates are machine-specific.) Use it to ask the *author* why, not to blame them. The commit message should answer.

**`git log -S`** (the "pickaxe") finds commits that added or removed a given piece of text. **`git log -p -- file`** shows every change to one file:

```text
$ git log -S'discount' --oneline
47562ec Add discount helper
$ git log --oneline -- price.py
47562ec Add discount helper
d45c12d Add with_tax helper
```

**`git bisect`** finds the commit that introduced a bug using binary search. You tell git one good commit and one bad one; it checks out the middle; you say good or bad; it halves the range again. With `bisect run`, a script answers for you. We build a history of six commits, where the file `state.txt` says `good` until commit 4 breaks it:

```text
$ cd ~/work
$ mkdir bis
$ cd bis
$ git init -q
$ for i in 1 2 3 4 5 6; do if [ $i -ge 4 ]; then v=bad; else v=good; fi; echo "$v $i" > state.txt; git add state.txt; git commit -q -m "Change $i"; done
$ git log --oneline
dc11dc4 Change 6
a3afc69 Change 5
bc86d3e Change 4
ee02c94 Change 3
8f7a486 Change 2
77ccc57 Change 1
```

The test is "exit with 0 if the file contains `good`". `grep -q good state.txt` does exactly that. Start bisect with the bad commit (`HEAD`) and a known good one (`HEAD~5`), then let it run:

```text
$ git bisect start HEAD HEAD~5
Bisecting: 2 revisions left to test after this (roughly 1 step)
[ee02c94e0e1582fd3c3d2ddc800af72d52fc3189] Change 3
$ git bisect run grep -q good state.txt
running 'grep' '-q' 'good' 'state.txt'
Bisecting: 0 revisions left to test after this (roughly 1 step)
[a3afc69437aedb12a2fc39fc7976942dd701a18e] Change 5
running 'grep' '-q' 'good' 'state.txt'
Bisecting: 0 revisions left to test after this (roughly 0 steps)
[bc86d3e4671e7054c25e59366cd2cefdabf837b6] Change 4
running 'grep' '-q' 'good' 'state.txt'
bc86d3e4671e7054c25e59366cd2cefdabf837b6 is the first bad commit
commit bc86d3e4671e7054c25e59366cd2cefdabf837b6
Author: Ada Learner <ada@example.com>
Date:   Sun Jan 11 03:00:00 2026 +0000

    Change 4

 state.txt | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)
bisect found first bad commit
$ git bisect reset
Previous HEAD position was bc86d3e Change 4
Switched to branch 'main'
```

Git found the first bad commit, `Change 4`, in only about three steps. For 1,000 commits it would need about ten. In a real project the script would be `python -m pytest tests/test_x.py` or any command that fails when the bug is present.

### 9.8 Try it

**Predict.** You ran `git reset --hard HEAD~3` on `main` by accident. You had also made an uncommitted edit to `README.md` just before. Which of these can you get back: (a) the three commits, (b) the README edit?

<details><summary>Answer</summary>

(a) Yes: `git reflog` shows the old tip and `git reset --hard 'HEAD@{1}'` moves back. (b) No. The edit was never saved in a commit or a stash, so git has no copy. The lesson: commit or stash before any risky command. `git stash` before an experiment is cheap insurance.

</details>

**Try it.** Build a repository with four commits. (1) Remove the last commit with `--soft`, then add a fifth file and recommit both together as one commit. (2) Make a bad commit and `revert` it. (3) Use `reset --hard` to remove the two newest commits, then recover them with `reflog`. Write down which step needs which command from the decision table.

## 10. Remotes and GitHub flow

### 10.1 What a remote is

Git is **distributed**: every clone holds the whole history. A **remote** is just another copy of the repository, usually on a server (GitHub, GitLab, a company machine), that people use to share work. By tradition the main remote is named **`origin`**.

The remote commands are few:

| Command | Meaning |
|---|---|
| `git clone url` | copy a repository, set up `origin` |
| `git fetch` | download new commits from the remote; **change nothing** of your work |
| `git pull` | `fetch` plus merge (or rebase) into your branch |
| `git push` | upload your commits |
| `git remote -v` | list remotes |

The remote branch is remembered locally as `origin/main`: a read-only bookmark that says "where `main` was on the server the last time I looked". It only moves when you fetch, pull or push.

### 10.2 Practising with a local "server"

You do not need GitHub to learn remotes. A **bare repository** (a repository without a working tree, which is what servers hold) in a local folder behaves like a remote. Create one, then two clones: you (`ada`) and a teammate (`ben`).

```text
$ cd ~/work
$ git init -q --bare server.git
$ git clone -q server.git ada
warning: You appear to have cloned an empty repository.
$ cd ada
$ mk start
$ git push -u origin main
To /home/you/work/server.git
 * [new branch]      main -> main
branch 'main' set up to track 'origin/main'.
$ git remote -v
origin	/home/you/work/server.git (fetch)
origin	/home/you/work/server.git (push)
$ git branch -vv
* main d626aa4 [origin/main] Add start
```

`git push -u origin main` uploads `main` and sets it to **track** `origin/main` (`-u` is "set upstream"). After that, plain `git push` and `git pull` know where to go. `git branch -vv` shows the tracking relation in brackets.

Now Ben clones the server and does some work. Ben has his own identity here (set only for this repository):

```text
$ cd ~/work
$ git clone -q server.git ben
$ cd ben
$ git config user.name "Ben Teammate"
$ git config user.email "ben@example.com"
$ git lg
* d626aa4 (HEAD -> main, origin/main, origin/HEAD) Add start
$ mk ben1
$ git push
To /home/you/work/server.git
   d626aa4..4305327  main -> main
```

Meanwhile Ada, who knows nothing of Ben's push, commits and tries to push:

```text
$ cd ~/work/ada
$ mk ada1
$ git push
To /home/you/work/server.git
 ! [rejected]        main -> main (fetch first)
error: failed to push some refs to '/home/you/work/server.git'
hint: Updates were rejected because the remote contains work that you do not
hint: have locally. This is usually caused by another repository pushing to
hint: the same ref. If you want to integrate the remote changes, use
hint: 'git pull' before pushing again.
hint: See the 'Note about fast-forwards' in 'git push --help' for details.
```

**Rejected.** Git refuses because the remote has a commit Ada does not have, and accepting her push would erase Ben's work from `main`. The message says exactly what to do: fetch (or pull) first. First, *look* before merging:

```text
$ git fetch
From /home/you/work/server
   d626aa4..4305327  main       -> origin/main
$ git lg
* 9ee7776 (HEAD -> main) Add ada1
| * 4305327 (origin/main, origin/HEAD) Add ben1
|/
* d626aa4 Add start
$ git status
On branch main
Your branch and 'origin/main' have diverged,
and have 1 and 1 different commits each, respectively.
  (use "git pull" if you want to integrate the remote branch with yours)

nothing to commit, working tree clean
```

`fetch` downloaded Ben's commit and moved `origin/main`, but did not touch Ada's own `main`. The graph shows the branches diverged. `status` says "have diverged, 1 and 1 different commits each". Now integrate. Two ways, as in section 7:

```text
git pull --no-rebase     # merge: creates a merge commit
git pull --rebase        # rebase: replays your commit on top of theirs
```

Most teams prefer `--rebase` for a clean line. You can make it the default with `git config --global pull.rebase true`.

```text
$ git pull --rebase
Rebasing (1/1)
Successfully rebased and updated refs/heads/main.
$ git lg
* 81735cc (HEAD -> main) Add ada1
* 4305327 (origin/main, origin/HEAD) Add ben1
* d626aa4 Add start
$ git push
To /home/you/work/server.git
   4305327..81735cc  main -> main
```

Ada's commit was replayed after Ben's, so the history is linear, and the push now succeeds. This "fetch, integrate, push" rhythm is the daily life of teamwork. Ben pulls to catch up:

```text
$ cd ~/work/ben
$ git pull
From /home/you/work/server
   4305327..81735cc  main       -> origin/main
Updating 4305327..81735cc
Fast-forward
 ada1.txt | 1 +
 1 file changed, 1 insertion(+)
 create mode 100644 ada1.txt
$ git log --oneline
81735cc Add ada1
4305327 Add ben1
d626aa4 Add start
```

### 10.3 Force pushes, safely

After you rebase or amend a commit that you already pushed (to your own feature branch), a normal push is rejected, because history changed. You must force it. **Always** use `--force-with-lease`, never plain `--force`:

```text
git push --force-with-lease
```

`--force-with-lease` means: "overwrite the remote branch only if it is still exactly where I last saw it". If someone pushed in the meantime, git refuses, instead of silently destroying their work. Plain `--force` has no such check. **Never force-push `main`.** Most hosts let you forbid it with branch protection.

### 10.4 What GitHub adds

GitHub (and GitLab, Bitbucket, Codeberg) is a remote with a web application around it:

- **Pull requests** (PRs; "merge requests" on GitLab): a page for proposing a merge, discussing it, and reviewing it.
- **Issues**: a to-do and bug list. A commit message with `Fixes #12` closes issue 12 when merged.
- **Actions / CI**: servers that run your tests on every push.
- **Branch protection**: rules such as "no direct pushes to `main`; need one approval; tests must pass".
- **Releases, Pages, Projects**: packages, websites, boards.

### 10.5 GitHub flow

GitHub flow is a very simple, popular way of working. Its rules:

1. `main` is **always deployable** (tests pass, it works).
2. To do anything, create a **branch from `main`** with a descriptive name.
3. Commit to your branch, **push it often**.
4. Open a **pull request** when you want feedback (even early, as a "draft").
5. Others **review**; you update the branch with more commits.
6. CI is green and a reviewer approves: **merge** into `main`.
7. Delete the branch. Deploy.

As a picture:

```text
main:       A ---------------------------- M        (always working)
             \                            /
feature:      B -- C -- D -- (review) -- E          (short-lived)
                       ^
                  open pull request
```

There are three ways to merge the PR button, and teams pick one:

| Button | Result | When it is good |
|---|---|---|
| **Merge commit** | keeps all commits and adds a merge commit | you want the full story |
| **Squash and merge** | all PR commits become **one** commit on `main` | branch had messy "wip" commits; one PR = one commit |
| **Rebase and merge** | PR commits replayed one by one, no merge commit | each commit is clean and meaningful |

Because squash is so common, the **PR title** often becomes the commit message on `main`. Write PR titles like commit summaries.

Other workflows exist (git-flow with `develop` and `release` branches, trunk-based development with very short branches). GitHub flow is the simplest and the one to use for your own projects.

**Forks.** In open source you usually cannot push to someone's repository. You **fork** it (your own copy on GitHub), push branches to your fork, and open a PR from your fork to the original ("upstream"). Locally you then have two remotes: `origin` (your fork) and `upstream` (the original).

### 10.6 A good pull request

- **Small.** Under about 400 lines of changes is reviewable; a 3,000-line PR gets a quick "looks fine" and hides bugs.
- **One purpose.** A bug fix and an unrelated refactor are two PRs.
- **A description** that says *what* and *why*, how you tested it, and what you want the reviewer to look at. Link the issue.
- **Tests** for the new behaviour.
- **Self-review first.** Read your own diff on the PR page before asking anyone. You will find silly mistakes.

A simple PR description template:

```text
## What
Add a `discount()` helper to the price module.

## Why
Sales needs percentage discounts (issue #12).

## How I tested
Added tests/test_price.py; `make check` is green.

## Notes for the reviewer
Please check the rounding rule in `discount()`.
```

### 10.7 Try it on your machine: your first pull request

> **This tutorial needs a GitHub account and internet, so its output is described, not captured.** Everything before and after it works offline. Outputs marked "expected" are what you should see; URLs, hashes and numbers will be yours. Use your **personal** account only for this course.

**Step 1. Create an empty repository on GitHub.** In the browser: New repository, name it `pr-practice`, tick nothing (no README), Create. GitHub shows a page with a URL like `https://github.com/YOUR-NAME/pr-practice.git`.

**Step 2. Prepare a local project and push it.**

```text
mkdir pr-practice && cd pr-practice
git init
echo "# PR practice" > README.md
git add README.md
git commit -m "Add README"
git branch -M main
git remote add origin https://github.com/YOUR-NAME/pr-practice.git
git push -u origin main
```

Expected: `git push` asks you to sign in (a browser window, a token, or an SSH key; GitHub's page "Connecting to GitHub" explains the options), then prints lines such as `Writing objects: 100% ...` and `branch 'main' set up to track 'origin/main'.` Refresh the GitHub page: your README appears.

**Step 3. Make a feature branch and push it.**

```text
git switch -c add-greeting
echo "Hello, reviewer!" >> README.md
git commit -am "Add a greeting to the README"
git push -u origin add-greeting
```

Expected: the output includes a line like `remote: Create a pull request for 'add-greeting' on GitHub by visiting:` followed by a URL.

**Step 4. Open the pull request.** Follow that URL (or press "Compare & pull request" on the repository page). Write a title in the commit-summary style, and a short description (what, why). Click "Create pull request". Look at the tabs: *Conversation*, *Commits*, *Files changed*.

**Step 5. Review your own PR.** In "Files changed", hover a line, press the blue `+`, and write a comment such as "Should this say Hello, world?". Press "Start a review", then "Submit review". You have now used the review tools (section 16).

**Step 6. Respond to the review.** Back in your terminal:

```text
sed -i 's/reviewer/world/' README.md
git commit -am "Greet the world instead"
git push
```

The PR updates by itself with the new commit.

**Step 7. Merge.** Press "Squash and merge", accept the message, confirm. Then "Delete branch".

**Step 8. Sync locally.**

```text
git switch main
git pull
git branch -d add-greeting
```

Expected: `git pull` shows `Fast-forward` and `1 file changed`. If `git branch -d` complains "not fully merged", that is normal after a *squash* merge: the squash commit has a different hash from your branch commits. Check that the content arrived and use `git branch -D add-greeting`.

You have completed the whole loop: branch, push, PR, review, merge, sync.

### 10.8 Try it

**Predict.** Ada pushes `main`. Ben, who last pulled yesterday, commits locally and runs `git push`. What happens, and what are the two commands to fix it?

<details><summary>Answer</summary>

Git rejects the push ("non-fast-forward", "fetch first") because the remote has commits Ben lacks. He runs `git pull --rebase` (or `git pull`) to bring them in and replay his commit on top, then `git push`.

</details>

## 11. Project structure and the `src` layout

### 11.1 Why structure matters

Core.13 showed how to make one package installable. A real project has more than one folder: the code, the tests, the docs, the configuration. If everyone puts them in different places, nobody can find anything and tools need custom setup. Python projects have settled on one shape:

```text
pricekit/                 <- the repository root (the project folder)
├── src/
│   └── pricekit/         <- the importable package
│       ├── __init__.py
│       └── core.py
├── tests/
│   └── test_core.py
├── pyproject.toml        <- name, version, dependencies, tool settings
├── README.md             <- the front door
├── CHANGELOG.md          <- what changed, per version
├── LICENSE
├── Makefile / tasks.py   <- one-word commands
└── .gitignore
```

Notice the **two** folders called `pricekit`: the outer one is the project (a name for humans and for git), the inner one `src/pricekit/` is the Python package (the name after `import`). Keep them different in your head.

### 11.2 Flat layout versus `src` layout

In a **flat layout** the package sits next to `pyproject.toml`, with no `src/` folder. It is simple and fine for small scripts. It has a quiet trap, which we can see directly:

```text
$ cd ~/work
$ cd flat
$ python -c "import pricekit; print(pricekit.with_tax(100))"
118.0
$ cd ../srcl
$ python -c "import pricekit; print(pricekit.with_tax(100))"
Traceback (most recent call last):
  File "<string>", line 1, in <module>
    import pricekit; print(pricekit.with_tax(100))
    ^^^^^^^^^^^^^^^
ModuleNotFoundError: No module named 'pricekit'
$ PYTHONPATH=src python -c "import pricekit; print(pricekit.with_tax(100))"
118.0
```

In the flat layout the package imports **without being installed**, because Python puts the current folder first on `sys.path` (core.13, section 4). In the `src` layout the same command fails until the package is installed (or `src` is put on the path explicitly, as in the last line).

That failure is a feature. With the flat layout, your tests pass on your machine **because they import the files in the folder**, even if the package is broken once installed (a forgotten sub-package, a missing data file, a wrong `pyproject.toml`). Then your user installs it and it does not work. With `src/`, you can only import what is **installed**, so the tests exercise what your users get. More reasons for `src/`:

- It separates **code** from **everything else** at a glance.
- Tools (build, lint, type check) can point at `src` and ignore the rest.
- It prevents accidentally importing a stale local copy.

The cost is one extra folder and, for tests, one line of configuration (`pythonpath = ["src"]` in section 12, or `pip install -e .`).

### 11.3 What goes where

| Folder or file | Holds | Rule |
|---|---|---|
| `src/<package>/` | the code users import | no tests, no scripts that need arguments |
| `tests/` | pytest tests, mirroring the package | `test_core.py` tests `core.py` |
| `docs/` | longer guides, only when README is not enough | |
| `scripts/` | one-off helper scripts | not part of the package |
| `pyproject.toml` | the single source of truth for metadata and tool settings | |
| `README.md` | what, why, install, use | section 15 |
| `LICENSE` | the legal terms (MIT is a common simple choice) | without one, others may not legally use your code |
| `.gitignore` | files git skips | section 4 |

Put a version in **one** place only. The usual choice is `version = "0.1.0"` in `pyproject.toml`; code that needs it reads it with `importlib.metadata.version("pricekit")`. Two copies will drift apart.

### 11.4 Try it

**Predict.** In the `src` layout, you run `pytest` from the project root but the tests say `ModuleNotFoundError: No module named 'pricekit'`. Name two ways to fix it.

<details><summary>Answer</summary>

(1) Install the project in editable mode into your virtual environment: `pip install -e .` (this needs the build tool downloaded once, so see the "Try it on your machine" box in section 12). (2) Tell pytest where the code is: `[tool.pytest.ini_options]` with `pythonpath = ["src"]` in `pyproject.toml`. This chapter's template uses (2) so everything works offline, and recommends (1) as soon as you can.

</details>

## 12. `pyproject.toml`, pytest, ruff and mypy

Core.13 explained `pyproject.toml` and the `[project]` table. Here we meet the **tool tables**: one file configures your build, your tests, your linter and your type checker. One file means one place to look. The full file is written in section 17; this section explains each part.

### 12.1 Project metadata

```toml
[build-system]
requires = ["setuptools>=77"]
build-backend = "setuptools.build_meta"

[project]
name = "pricekit"
version = "0.1.0"
description = "Small price helpers: tax and discounts."
readme = "README.md"
requires-python = ">=3.11"
license = "MIT"
dependencies = []                     # what users need at run time

[project.optional-dependencies]
dev = ["pytest>=8", "mypy>=1.10", "ruff>=0.5"]   # what developers need

[project.scripts]
pricekit = "pricekit.cli:main"        # creates a `pricekit` command
```

Runtime dependencies and developer tools are **separate on purpose**. A user who installs `pricekit` does not need `pytest`. A developer runs `pip install -e ".[dev]"` and gets both. With `dependencies = []` your library is fully standard-library, which is the best kind to depend on.

### 12.2 pytest

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
addopts = "-ra"
```

- `testpaths`: where to look, so a bare `pytest` finds only your tests.
- `pythonpath`: extra folders for imports. Here it makes the `src` layout work without installation.
- `addopts`: options always added. `-ra` prints a short summary of everything that did not pass.

Test files are named `test_*.py`; test functions `test_*`. One test checks one behaviour, with a name that reads like a sentence: `test_discount_of_zero_percent_keeps_the_price`. Run them with `python -m pytest`; using `python -m` guarantees the pytest of **this** environment (core.13).

### 12.3 ruff: a fast linter and formatter

A **linter** reads code without running it and reports likely mistakes and style problems: unused imports, undefined names, lines too long. A **formatter** rewrites code to one agreed style so that nobody argues about quotes and spaces. `ruff` does both, very quickly, in one tool. It is a third-party program, so it needs `pip install ruff`.

```toml
[tool.ruff]
line-length = 88
src = ["src", "tests"]

[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP"]
```

| Code | Rule family |
|---|---|
| `E` | pycodestyle errors (indentation, spaces) |
| `F` | pyflakes: unused imports and variables, undefined names |
| `I` | import order (isort rules) |
| `B` | bugbear: likely bugs, such as a mutable default argument |
| `UP` | pyupgrade: old syntax that has a modern form |

Commands: `ruff check .` (lint), `ruff check --fix .` (apply safe fixes), `ruff format .` (reformat), `ruff format --check .` (only report). A reasonable team rule: **formatting is never discussed in review; the tool decides.**

### 12.4 mypy: check the types

You will meet type hints in depth later in the course. For now: `def with_tax(price: float) -> float:` tells readers and tools what goes in and out. `mypy` reads these hints and finds bugs like passing a string where a number is expected, *without running the code*.

```toml
[tool.mypy]
python_version = "3.11"
strict = true
files = ["src"]
```

`strict = true` turns on all the checks; you can relax it for old code. Start strict on a new project; it is much easier than adding it later.

### 12.5 Try it on your machine: install the tools and the project

> **Needs the internet** (to download `ruff` and the build tool), so the output is described, not captured.

```text
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
python -m pip install -e ".[dev]"
ruff --version
ruff check .
ruff format --check .
```

Expected: `pip` builds and installs `pricekit` in editable mode (a final line like `Successfully installed pricekit-0.1.0 ...`), then installs `pytest`, `mypy` and `ruff`. `ruff check .` prints `All checks passed!` on clean code. `ruff format --check .` prints `N files already formatted`. After an editable install, `import pricekit` works from any folder while the venv is active, and changes in `src/` are visible at once.

### 12.6 Try it

**Predict.** `ruff check` reports `F401 'os' imported but unused`. Is the code wrong? What do you do?

<details><summary>Answer</summary>

The program still runs; the report is about clutter and a possible leftover from earlier code. Delete the import. If the import is intended (for example re-exporting a name in `__init__.py`), say so with `__all__` or a comment `# noqa: F401`, so the next reader knows it is deliberate.

</details>

## 13. Task runners: Makefile and pure Python

### 13.1 The problem

A project has many commands: run tests, check style, check types, build, clean. Each has options. Nobody remembers them all, and the README gets long. A **task runner** gives each job a short name: `make test`, `make check`. The same names work for you, for a new teammate, for pre-commit and for CI.

### 13.2 Make in ten minutes

`make` is an old tool, installed on Linux and macOS (on Windows you can get it through Git Bash, MSYS2, WSL or `choco install make`). A `Makefile` is a list of **rules**:

```text
target: prerequisites
<TAB>recipe line (a shell command)
```

**Important:** recipe lines must start with a real **TAB** character, not spaces. This is the most common Makefile error ("missing separator"). Configure your editor to keep tabs in Makefiles.

Make's original idea is "rebuild only what is out of date". Watch it work with a file target:

```make
out.txt: in.txt
	cp in.txt out.txt
	echo "built out.txt"
```

```text
$ make
cp in.txt out.txt
echo "built out.txt"
built out.txt
$ make
make: 'out.txt' is up to date.
$ touch in.txt
$ make
cp in.txt out.txt
echo "built out.txt"
built out.txt
```

First run: `out.txt` does not exist, so make runs the recipe. Second run: `out.txt` is newer than `in.txt`, so nothing to do. After `touch in.txt` (which updates its timestamp) the target is out of date and is rebuilt. (Make echoes each recipe line as it runs it; put `@` in front of a line to hide the echo.)

### 13.3 Phony targets and variables

Our project tasks do not make files. `test` is a *name*, not a file. If a file called `test` existed, make would think it was up to date and do nothing. We declare such targets **phony**. We also use **variables** so the Python is named once:

```make
PYTHON ?= python

.PHONY: help test lint

help:  ## show this help
	@grep -E '^[a-z]+:.*##' $(MAKEFILE_LIST) | sed 's/:.*## /  /'

test:  ## run the tests
	@echo "running tests with $(PYTHON)"
	$(PYTHON) -c "print('tests would run here')"

lint: test  ## run lint (needs test first)
	@echo "lint ok"
```

```text
$ make help
help  show this help
test  run the tests
lint  run lint (needs test first)
$ make lint
running tests with python
python -c "print('tests would run here')"
tests would run here
lint ok
$ make test PYTHON=python3
running tests with python3
python3 -c "print('tests would run here')"
tests would run here
```

- `PYTHON ?= python` sets the variable only if the user has not set it. `make test PYTHON=python3` overrides it from the command line.
- `$(PYTHON)` uses the variable.
- `.PHONY` lists targets that are names, not files.
- `lint: test` means `lint` **depends on** `test`: make runs `test` first. Dependencies are how `make check` can mean "lint, then types, then tests".
- The `## text` comments plus a small `grep` make a self-documenting `make help`, a habit worth copying.
- `make` exits with an error if any recipe line fails, which is what CI needs.

Make has more (pattern rules, functions, `$@` automatic variables), but for project tasks these few pieces are enough.

### 13.4 A pure-Python task runner

Make is not installed everywhere, especially on Windows, and its syntax is its own small language. Since every Python developer already has Python, we can write the task runner **in Python**: one file `tasks.py`, run as `python tasks.py test`. It works the same on Linux, macOS and Windows, it can use all of Python, and you can read it. The core of it is only a dictionary from names to functions:

```python
"""Tiny task runner: python tasks.py <task>"""
import subprocess
import sys


def run(*cmd):
    print("+", "python", *cmd[1:], flush=True)
    code = subprocess.call(cmd)
    if code != 0:
        sys.exit(code)


def test():
    """run the tests"""
    run(sys.executable, "-c", "print('tests would run here')")


def lint():
    """run lint"""
    test()
    print("lint ok")


TASKS = {"test": test, "lint": lint}


def main(argv):
    if len(argv) != 2 or argv[1] not in TASKS:
        print("usage: python tasks.py <task>")
        for name, fn in TASKS.items():
            print(f"  {name:6} {fn.__doc__}")
        return 2
    TASKS[argv[1]]()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
```

```text
$ python tasks.py
usage: python tasks.py <task>
  test   run the tests
  lint   run lint
$ python tasks.py lint
+ python -c print('tests would run here')
tests would run here
lint ok
$ python tasks.py nothing; echo "exit code: $?"
usage: python tasks.py <task>
  test   run the tests
  lint   run lint
exit code: 2
```

Compare with the Makefile: each task is a function, a dependency is just a function call, `sys.executable` is "the Python that is running me" (so it always uses the right virtual environment), and a failing command stops the run with its exit code. Section 17 writes the real one for the project template, with `check`, `fmt` and `clean`.

A related trick needs no file at all: give every tool as a module call, `python -m pytest`, `python -m mypy`, `python -m ruff` (if installed). This is already portable.

### 13.5 Other runners (a short tour)

| Tool | Idea | When |
|---|---|---|
| **make** | rules and file timestamps | Linux/macOS projects; very common |
| **tasks.py** (hand-made) | functions in Python | zero dependencies, any OS |
| **just** | like make but without file rules, friendlier syntax, separate program | many polyglot projects |
| **nox** / **tox** | create fresh virtual environments and run tests in each (several Python versions) | libraries that support many Pythons |
| **invoke** | tasks.py with a library | when your hand-made file grows |

None of them is "the right one". Pick one, put its commands in the README, and keep the **names** the same across projects (`test`, `lint`, `fmt`, `check`, `clean`). A person who knows your names can use any of your projects.

### 13.6 Try it

**Predict.** A Makefile recipe line is indented with four spaces. What does `make` print?

<details><summary>Answer</summary>

```text
$ cd ~/work/mk
$ printf 'bad:\n    echo hi\n' > Makefile.bad
$ make -f Makefile.bad bad
Makefile.bad:2: *** missing separator.  Stop.
```

`missing separator`: make needs a TAB, and (on the first recipe) tries to read your spaces as a new rule. The fix is to replace the leading spaces with one tab.

</details>

## 14. Git hooks and pre-commit

### 14.1 The idea: catch it before it is committed

Lint errors and failing tests are cheapest to fix **before** they reach the shared history. Git can run a program at certain moments; these are **hooks**. The most useful is `pre-commit`: it runs when you type `git commit`, and if it exits with an error, the commit is cancelled. A hook is just an executable file named for the event in `.git/hooks/`. We can write one by hand and see exactly how it works:

```text
#!/bin/sh
# Refuse to commit a leftover debugger call.
if git diff --cached -U0 | grep -q '^+.*breakpoint()'; then
    echo "pre-commit: remove the breakpoint() call before committing"
    exit 1
fi
```

```text
$ chmod +x .git/hooks/pre-commit
$ echo 'breakpoint()' > app.py
$ git add app.py
$ git commit -m "Add app"; echo "exit code: $?"
pre-commit: remove the breakpoint() call before committing
exit code: 1
$ echo 'print("hi")' > app.py
$ git add app.py
$ git commit -q -m "Add app"
$ git log --oneline
f7c4a0f Add app
```

The first commit was cancelled with our message; the second passed. In an emergency `git commit --no-verify` skips hooks, so hooks are a **help, not a wall**. The wall is CI, which checks the same things on the server where nobody can skip them.

Plain hooks have a weakness: `.git/hooks/` is **not** part of the repository, so teammates do not receive it.

### 14.2 The `pre-commit` framework

The tool called **pre-commit** fixes that. You list the checks you want in a file `.pre-commit-config.yaml` which *is* committed. Everyone runs `pre-commit install` once, and the hooks then run automatically on the changed files.

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.6.9
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: end-of-file-fixer
      - id: trailing-whitespace
      - id: check-added-large-files
```

**Try it on your machine** (needs the network to fetch the hook programs, so the output is described):

```text
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

Expected: the first run downloads and builds the hook environments (it takes a minute), then prints a table with a line per hook ending in `Passed`, `Failed` or `Skipped`. When a hook fixes files (trailing whitespace, formatting), it reports `Failed` and modifies them: stage the changes and commit again. The `rev` values above are examples; use `pre-commit autoupdate` to get current ones.

### 14.3 Which checks belong where?

| Where | What | Why |
|---|---|---|
| Editor | format on save, live lint | instant feedback |
| pre-commit hook | fast checks: format, lint, whitespace, secrets | cheap, local |
| `make check` | everything, including tests and types | the one command to trust |
| CI | the same `make check`, on a clean machine | cannot be skipped |

The golden rule: **CI runs the same command you run locally.** Never write checks twice in two different ways.

### 14.4 Try it

**Predict.** You wrote a `pre-commit` hook, committed it in `.git/hooks/`, and pushed. Your teammate clones the project. Does her `git commit` run your hook?

<details><summary>Answer</summary>

No. Files under `.git/` are never part of the repository, so cloning does not copy them. That is exactly why teams use the `pre-commit` framework (its config file is committed) or a documented command such as `make hooks`.

</details>

## 15. Writing documentation

### 15.1 Who reads what

Code is read far more often than it is written. There are four kinds of readers, and each needs a different text:

| Reader | Question | Where the answer lives |
|---|---|---|
| New visitor | "What is this? Is it for me?" | **README** (top) |
| New user | "How do I install and use it?" | README, then a `docs/` guide |
| Developer using your functions | "What does this function take and return?" | **docstrings** |
| Maintainer or reviewer | "What changed, and why?" | **CHANGELOG**, commit messages, PR descriptions |

Documentation that is out of date is worse than none. So keep it **close to the code** (docstrings, README in the repo) and **test it** where you can.

### 15.2 The README: the front door

The README is the first (often the only) file people read. A good one answers five questions in this order:

1. **What is it?** One sentence under the title.
2. **Why / what does it look like?** A tiny example that works.
3. **How do I install it?** Exact commands.
4. **How do I use it?** The two or three most common things.
5. **How do I work on it?** Setup, run tests, project layout, how to contribute, the license.

Rules of thumb: put the **most important thing first**; show code, not adjectives; every command must be copy-paste ready; test your README by following it on a clean machine (or ask a friend to). A README written as a story of how you built it is a diary, not a README. The full README for our template is in section 17.

### 15.3 Docstrings

A **docstring** is a string literal as the first statement of a module, function or class. Tools show it: `help()`, editors, documentation generators. Write what a user needs: what the function does, its arguments, what it returns, what it raises. Do not repeat the code in words.

```text
$ cd ~/work/doc
$ python -c "import demo; help(demo.mean)"
Help on function mean in module demo:

mean(values)
    Return the arithmetic mean of ``values``.

    Args:
        values: a non-empty list of numbers.

    Returns:
        The mean as a float.

    Raises:
        ValueError: if ``values`` is empty.

    >>> mean([1, 2, 3, 4])
    2.5
$ python -m doctest -v demo.py
Trying:
    mean([1, 2, 3, 4])
Expecting:
    2.5
ok
1 item had no tests:
    demo
1 item passed all tests:
   1 test in demo.mean
1 test in 2 items.
1 passed.
Test passed.
```

- The first line is a **one-sentence summary** in the imperative ("Return ...").
- The **Args / Returns / Raises** layout is the "Google style"; "NumPy style" and reStructuredText are the other common ones. Choose one per project.
- The `>>>` example is a **doctest**: Python (or pytest with `--doctest-modules`) runs it and checks the output. A wrong example fails the tests, so the documentation cannot rot unnoticed.
- Comments (`# ...`) explain *why* something odd is done. Docstrings explain *what* for the outside user. Prefer clear names over comments that restate code.

### 15.4 The CHANGELOG

A `CHANGELOG.md` lists what changed in each release, for humans. The common format is [Keep a Changelog](https://keepachangelog.com): newest first, an `Unreleased` section on top, and groups `Added`, `Changed`, `Fixed`, `Removed`, `Deprecated`, `Security`. It is **not** a dump of `git log`: git log has every typo fix; the changelog has what a user cares about.

Versions follow **semantic versioning**, `MAJOR.MINOR.PATCH`:

| Increase | When | Example |
|---|---|---|
| MAJOR | you break compatibility (a function is removed or behaves differently) | 1.4.2 to 2.0.0 |
| MINOR | you add a feature, nothing breaks | 1.4.2 to 1.5.0 |
| PATCH | you fix a bug, nothing else | 1.4.2 to 1.4.3 |

Before 1.0.0 (`0.x.y`) anything may change; it means "still experimental".

Release routine: move the `Unreleased` entries under a new heading with the version and date, change `version` in `pyproject.toml`, commit (`Release 0.2.0`), and create a git **tag** so the commit has a permanent name:

```text
$ cd ~/work/pick
$ git tag -a v0.2.0 -m "Release 0.2.0"
$ git tag
v0.2.0
$ git describe
v0.2.0
```

An annotated tag (`-a`) is a named, permanent pointer with a message; it is how a release is marked in git. Push tags with `git push --tags`.

### 15.5 Try it

**Predict.** You fix a typo in an error message and add a new optional argument to a function, with no other changes. From version 1.2.3, what is the next version?

<details><summary>Answer</summary>

`1.3.0`. Adding a backwards-compatible feature raises MINOR, and it resets PATCH to 0. The typo fix alone would have been a PATCH, but the highest-level change in the release decides.

</details>

## 16. Code review

### 16.1 Why review?

Review is not about catching the author being foolish. It has four jobs: **find bugs** a second pair of eyes sees, **share knowledge** (two people now know this code), **keep the style and design consistent**, and **teach** both sides. Studies and experience agree: reviewed code has fewer defects, and teams that review learn faster. You will review and be reviewed for your whole career, so it is a skill to practise.

### 16.2 Reviewing locally with git

You do not need GitHub to read a branch. Two commands tell you everything:

```text
$ cd ~/work/pick
$ git log --oneline main..experiment
253b5f4 Add Y
a8138ca Fix rounding bug
1cb00e3 Add X
$ git diff --stat main...experiment
 X.txt      | 1 +
 Y.txt      | 1 +
 hotfix.txt | 1 +
 3 files changed, 3 insertions(+)
```

`main..experiment` means "commits in `experiment` that are not in `main`". `main...experiment` (three dots) in `diff` means "changes on `experiment` since it split from `main`", which is the same view a pull request shows. Commit-by-commit reading (`git log -p main..experiment`) is easier when commits are small and well named, another reason to write them that way.

### 16.3 How to review: the author's side first

Before you ask anyone, review **your own** diff as if you were a stranger. Read it top to bottom. Remove debugging prints, stray files, commented-out code. Check that each change belongs to the purpose of the PR. Run the tests. Half of review comments disappear this way.

### 16.4 How to review other people's code

Read in this order:

1. **The description and the issue.** What is this meant to do?
2. **The tests.** Do they describe the behaviour? Do they cover edge cases (empty, zero, negative, very large)?
3. **The design.** Is the change in the right place? Is something duplicated? Will it be hard to change later?
4. **The details.** Names, error handling, unclear code, off-by-one errors, security (user input, secrets, file paths).
5. **The small stuff** (formatting, typos), which should be automated by ruff, not discussed by humans.

A checklist you can keep in mind:

| Question | Looking for |
|---|---|
| Does it do what it says? | wrong logic, missing cases |
| Is it tested? | no tests, tests that cannot fail |
| Can I understand it in one read? | clever tricks, long functions, unclear names |
| What can go wrong? | exceptions, empty input, files that do not exist |
| Is it safe? | secrets in code, unvalidated input, SQL or shell injection |
| Is the change the right size? | unrelated edits mixed in |
| Are docs and changelog updated? | behaviour changed, README unchanged |

### 16.5 How to write a comment

Comments are read by a person who worked hard. Make them useful and kind:

- **Comment on the code, not the person.** "This loop is O(n squared)" not "you wrote a slow loop".
- **Ask questions.** "What happens if the list is empty?" gives the author a chance to explain or notice.
- **Explain why**, and suggest an alternative: "A `set` would make the membership test O(1)."
- **Label the weight.** Say what is required and what is optional:
  - `blocking:` must be fixed before merge.
  - `suggestion:` I would do it this way; your call.
  - `nit:` tiny preference; ignore if you disagree.
  - `question:` I do not understand; no change requested.
- **Praise good work.** "Nice test for the empty case." People repeat what is noticed.

| Weak | Better |
|---|---|
| "This is wrong." | "`discount(100, 150)` returns -50. Should this raise `ValueError`? (blocking)" |
| "Why did you do it like this?" | "I find the nested loop hard to follow. Would a dict of counts be clearer? (suggestion)" |
| "Use better names." | "nit: `d` could be `discount_percent`." |

### 16.6 How to receive a review

Your code is not you. A comment is about the change, and a bug found in review is a bug not found by a customer. So:

- **Say thanks, assume good intent.** Tone is hard to read in text.
- **Do not take it personally; do not defend instantly.** Read the comment twice. If it is right, fix it. If you disagree, explain your reasoning calmly, or ask a question.
- **Answer every comment**: fix it and say "done", or explain why not. Never leave one hanging.
- **Push fixes as new commits during review** (reviewers can see what changed), and tidy at the end (squash on merge).
- **Disagree and move on.** If you still disagree after one round, ask a third person, or accept the decision and note it. The goal is working software, not winning.
- **Keep it small next time.** Large PRs get shallow reviews.

### 16.7 Try it

**Predict.** A reviewer writes: "Why on earth is this a global variable?" Rewrite it as a good review comment, and label its weight.

<details><summary>Answer</summary>

For example: "`CACHE` is a module-level global, so tests can affect each other through it. Could we pass the cache in as an argument, or reset it in a fixture? (suggestion)". It names the code, gives a reason, proposes an alternative and says how strong the request is.

</details>

## 17. Project: the professional project template

Now we put everything together. We build a small but complete project, **`pricekit`**, step by step, with a clean history. Every later project in this course starts as a copy of it. The steps are: repository and housekeeping, the package, tests, configuration, task runner, documentation, automation, and finally a **fresh clone test** that proves a stranger can set it up in minutes.

All commands run in the practice folder `~/work`. Create the files exactly as shown.

### 17.1 Step 1: the repository and housekeeping

```text
$ cd ~/work
$ mkdir -p pricekit/src/pricekit pricekit/tests
$ cd pricekit
$ git init -q
$ cp ../shop/.gitignore .
$ ls -a
.
..
.git
.gitignore
src
tests
```

We reuse the `.gitignore` from section 4. A project also needs a `LICENSE`. Without one, nobody may legally reuse your code. MIT is a short, permissive, popular choice. Copy its text from [choosealicense.com](https://choosealicense.com/licenses/mit/) and put your name and year in it; the template's `LICENSE` starts like this:

```text
MIT License

Copyright (c) 2026 Ada Learner

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, ... (the rest of the standard MIT text)
```

(The `...` is only a shortening for this book; your file must contain the full standard text.)

```text
$ git add .gitignore LICENSE
$ git commit -q -m "Add .gitignore and MIT license"
```

### 17.2 Step 2: the package, `src` layout

The package has two modules. `core.py` holds the logic, `__init__.py` decides the public names. `py.typed` is an empty marker file that tells type checkers "this package has type hints".

```python
"""Price calculations: tax and discounts."""

TAX_RATE = 0.18


def with_tax(price: float, rate: float = TAX_RATE) -> float:
    """Return ``price`` plus tax, rounded to two decimals.

    >>> with_tax(100)
    118.0
    """
    if price < 0:
        raise ValueError("price must not be negative")
    return round(price * (1 + rate), 2)


def discount(price: float, percent: float) -> float:
    """Return ``price`` reduced by ``percent`` per cent.

    >>> discount(200, 25)
    150.0
    """
    if not 0 <= percent <= 100:
        raise ValueError("percent must be between 0 and 100")
    return round(price * (1 - percent / 100), 2)
```

```python
"""pricekit: small price helpers."""

from pricekit.core import discount, with_tax

__all__ = ["discount", "with_tax"]
```


### 17.3 Step 3: the tests

Tests mirror the package: `tests/test_core.py` tests `core.py`. Names read like sentences.

```python
import pytest

from pricekit import discount, with_tax


def test_with_tax_adds_the_default_rate():
    assert with_tax(100) == 118.0


def test_with_tax_rounds_to_two_decimals():
    assert with_tax(19.99) == 23.59


def test_with_tax_rejects_a_negative_price():
    with pytest.raises(ValueError):
        with_tax(-1)


def test_discount_of_zero_percent_keeps_the_price():
    assert discount(80, 0) == 80


def test_discount_takes_percent_off():
    assert discount(200, 25) == 150


def test_discount_rejects_more_than_100_percent():
    with pytest.raises(ValueError):
        discount(100, 150)
```

### 17.4 Step 4: `pyproject.toml`

All the metadata and tool settings in one file (explained in sections 11 and 12):

```toml
[build-system]
requires = ["setuptools>=77"]
build-backend = "setuptools.build_meta"

[project]
name = "pricekit"
version = "0.1.0"
description = "Small price helpers: tax and discounts."
readme = "README.md"
requires-python = ">=3.11"
license = "MIT"
dependencies = []

[project.optional-dependencies]
dev = ["pytest>=8", "mypy>=1.10", "ruff>=0.5"]

# Optional: a command-line entry point
# [project.scripts]
# pricekit = "pricekit.cli:main"

[tool.setuptools.package-data]
pricekit = ["py.typed"]

[tool.pytest.ini_options]
testpaths = ["tests", "src"]
pythonpath = ["src"]
addopts = "-ra -q --doctest-modules"

[tool.ruff]
line-length = 88
src = ["src", "tests"]

[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP"]

[tool.mypy]
python_version = "3.11"
strict = true
files = ["src"]
```

`testpaths` includes `src` so that the doctests in the docstrings run too. Now run the tests with pytest, and the type checker:

```text
$ python -m pytest
........                                                                 [100%]
8 passed in 0.27s
$ python -m mypy
Success: no issues found in 2 source files
```

(Timings such as `0.01s`, and the mypy version, are machine-specific. The cache folders `.pytest_cache` and `.mypy_cache` appeared, and `.gitignore` already hides them.) We have 6 tests plus 2 doctests = 8 passing items. Commit the package, tests and configuration together, because they only make sense together:

```text
$ git status --short
?? pyproject.toml
?? src/
?? tests/
$ git add pyproject.toml src tests
$ git commit -q -m "Add pricekit package with tests and tool settings"
```

The build metadata names `README.md`, which we write in step 6; until then an *install* would fail, but the tests do not need an install.

### 17.5 Step 5: the task runner

One file, no dependencies, works on every operating system. The names (`test`, `lint`, `types`, `fmt`, `check`, `clean`) are the ones you will use in every project.

```python
"""Project tasks.  Usage: python tasks.py <task>   (no argument lists them)."""

import importlib.util
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent


def run(*cmd: str) -> None:
    """Run a command in the project folder; stop at the first failure."""
    print("+", "python", *cmd[1:], flush=True)
    code = subprocess.call(cmd, cwd=ROOT)
    if code != 0:
        sys.exit(code)


def tool(name: str) -> list[str]:
    """Command prefix for a tool installed in the current environment."""
    if importlib.util.find_spec(name) is None:
        sys.exit(f"{name} is not installed. Run: python -m pip install -e '.[dev]'")
    return [sys.executable, "-m", name]


def test() -> None:
    """run the tests"""
    run(*tool("pytest"))


def types() -> None:
    """check type hints with mypy"""
    run(*tool("mypy"))


def lint() -> None:
    """check style and common mistakes with ruff"""
    run(*tool("ruff"), "check", ".")
    run(*tool("ruff"), "format", "--check", ".")


def fmt() -> None:
    """fix style problems automatically"""
    run(*tool("ruff"), "check", "--fix", ".")
    run(*tool("ruff"), "format", ".")


def check() -> None:
    """everything CI runs: lint, types, tests"""
    lint()
    types()
    test()


def clean() -> None:
    """delete caches and build output"""
    for name in (".pytest_cache", ".mypy_cache", ".ruff_cache", "build", "dist"):
        shutil.rmtree(ROOT / name, ignore_errors=True)
    for path in ROOT.rglob("__pycache__"):
        shutil.rmtree(path, ignore_errors=True)
    print("cleaned")


TASKS = {fn.__name__: fn for fn in (test, types, lint, fmt, check, clean)}


def main(argv: list[str]) -> int:
    if len(argv) != 2 or argv[1] not in TASKS:
        print("usage: python tasks.py <task>")
        for name, fn in TASKS.items():
            print(f"  {name:6} {fn.__doc__}")
        return 2
    TASKS[argv[1]]()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
```

For people who like `make`, a Makefile with the same names that simply **forwards** to `tasks.py`, so the logic exists once:

```make
PYTHON ?= python

.PHONY: help test lint types fmt check clean

help:  ## show this help
	@grep -E '^[a-z]+:.*##' $(MAKEFILE_LIST) | sed 's/:.*## /  /'

test:  ## run the tests
	$(PYTHON) tasks.py test

lint:  ## check style with ruff
	$(PYTHON) tasks.py lint

types:  ## check types with mypy
	$(PYTHON) tasks.py types

fmt:  ## fix style automatically
	$(PYTHON) tasks.py fmt

check:  ## run everything CI runs
	$(PYTHON) tasks.py check

clean:  ## delete caches and build output
	$(PYTHON) tasks.py clean
```

```text
$ python tasks.py
usage: python tasks.py <task>
  test   run the tests
  types  check type hints with mypy
  lint   check style and common mistakes with ruff
  fmt    fix style problems automatically
  check  everything CI runs: lint, types, tests
  clean  delete caches and build output
$ python tasks.py test
+ python -m pytest
........                                                                 [100%]
8 passed in 0.27s
$ make help
help  show this help
test  run the tests
lint  check style with ruff
types  check types with mypy
fmt  fix style automatically
check  run everything CI runs
clean  delete caches and build output
$ make types
python tasks.py types
+ python -m mypy
Success: no issues found in 2 source files
$ python tasks.py lint; echo "exit code: $?"
ruff is not installed. Run: python -m pip install -e '.[dev]'
exit code: 1
$ python tasks.py clean
cleaned
```

Look at the `lint` line. On the test machine `ruff` was not installed, and the runner said so with the exact fix instead of a confusing traceback. On a machine set up with `pip install -e ".[dev]"` it runs ruff. Good error messages are part of a professional project.

```text
$ git add tasks.py Makefile
$ git commit -q -m "Add task runner (tasks.py) and Makefile front end"
```

### 17.6 Step 6: README and CHANGELOG

The README follows the five questions of section 15. (Its code samples are shown indented instead of fenced, so that this book can display the whole file inside one block; in your own README use the usual triple-backtick fences.)

```markdown
# pricekit

Small, dependency-free price helpers: add tax and take discounts.

    >>> from pricekit import discount, with_tax
    >>> with_tax(100)
    118.0
    >>> discount(200, 25)
    150.0

## Install

    python -m pip install .

Needs Python 3.11 or newer.

## Use

- `with_tax(price, rate=0.18)` returns the price plus tax, rounded to 2 decimals.
- `discount(price, percent)` returns the price reduced by `percent` per cent.

Both raise `ValueError` for impossible input (negative price, percent outside 0 to 100).

## Develop

    python -m venv .venv
    source .venv/bin/activate        # Windows: .venv\Scripts\activate
    python -m pip install -e ".[dev]"
    python tasks.py check            # lint, types, tests (or: make check)

| Task | Meaning |
|---|---|
| `test` | run the tests (and the docstring examples) |
| `lint` / `fmt` | check / fix style |
| `types` | check type hints |
| `clean` | delete caches |

## Project layout

    src/pricekit/   the package
    tests/          pytest tests
    tasks.py        task runner (Makefile forwards to it)

## Contributing

Branch from `main`, keep commits small, run `python tasks.py check`, open a pull request.

## License

MIT, see [LICENSE](LICENSE).
```

```markdown
# Changelog

All notable changes are listed here. The format follows
[Keep a Changelog](https://keepachangelog.com) and the project uses
[semantic versioning](https://semver.org).

## [Unreleased]

## [0.1.0] - 2026-01-15

### Added
- `with_tax` and `discount` helpers.
- Tests, type hints, task runner.
```

```text
$ git add README.md CHANGELOG.md
$ git commit -q -m "Add README and CHANGELOG"
```

### 17.7 Step 7: automation files

Two files that need outside services to *run* (so we only write them): the pre-commit configuration from section 14, and a GitHub Actions workflow for **continuous integration (CI)**: on every push and pull request a fresh machine installs the project and runs `python tasks.py check`, the exact command you run locally.

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:

jobs:
  check:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.12", "3.13"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - run: python -m pip install -e ".[dev]"
      - run: python tasks.py check
```

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.6.9
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: end-of-file-fixer
      - id: trailing-whitespace
```

(The versions `rev` and the action versions are examples that were current when this was written. Update them.)

```text
$ git add .github .pre-commit-config.yaml
$ git commit -q -m "Add CI workflow and pre-commit config"
$ git lg
* b53cc2e (HEAD -> main) Add CI workflow and pre-commit config
* 8732c87 Add README and CHANGELOG
* c11b1a3 Add task runner (tasks.py) and Makefile front end
* ae6463e Add pricekit package with tests and tool settings
* 7d3fe1c Add .gitignore and MIT license
$ git ls-files
.github/workflows/ci.yml
.gitignore
.pre-commit-config.yaml
CHANGELOG.md
LICENSE
Makefile
README.md
pyproject.toml
src/pricekit/__init__.py
src/pricekit/core.py
src/pricekit/py.typed
tasks.py
tests/test_core.py
```

Notice the shape of these five commits: each has **one purpose**, a message in the imperative, and (from the second commit on) a working project. That is the history a reviewer enjoys.

### 17.8 Step 8: the fresh clone test

The final exam of any project: can a stranger get it working? Clone it into a new folder (as if from GitHub) and run the tasks:

```text
$ cd ~/work
$ git clone -q pricekit stranger
$ cd stranger
$ python tasks.py test
+ python -m pytest
........                                                                 [100%]
8 passed in 0.27s
$ python tasks.py types
+ python -m mypy
Success: no issues found in 2 source files
```

It works from a clean clone with no manual steps (beyond having Python, pytest and mypy; with the `.venv` setup of the README, `pip install -e ".[dev]"` supplies them). If something is missing, a stranger would have had to ask you, so **fix the README or the project, not the stranger**.

### 17.9 Try it on your machine: install it for real

> **Needs the internet** (the build tool, and the dev tools, are downloaded), so output is described.

```text
cd pricekit
python -m venv .venv && source .venv/bin/activate
python -m pip install -e ".[dev]"
python tasks.py check
python -c "import pricekit; print(pricekit.with_tax(100))"
```

Expected: `pip` ends with `Successfully installed ... pricekit-0.1.0 ...`; `python tasks.py check` prints each command with a leading `+`, ruff says `All checks passed!` and `N files already formatted`, mypy says `Success: no issues found in 2 source files`, and pytest ends with `8 passed`. The last line prints `118.0` from any folder, because the package is installed. If ruff wants to reformat a file, run `python tasks.py fmt` and commit the result.

### 17.10 Using the template for every project

Copy the folder, delete the history, rename the package, start fresh:

```text
cp -r pricekit myproject && cd myproject
rm -rf .git .venv && git init
# rename src/pricekit -> src/myproject, update pyproject.toml, README, tests
```

(Or publish `pricekit` on GitHub and mark it as a **template repository**; a "Use this template" button then creates new projects from it.) In each new project you change: the name (three places: folder under `src/`, `name` in `pyproject.toml`, the imports), the description, the README, the license year, and you empty the CHANGELOG's entries. Everything else stays. That is the point of a template.

### 17.11 Try it

**Predict.** In the template, a teammate adds a new module `src/pricekit/cart.py` but forgets to add tests. Which of our tools notices, and which does not?

<details><summary>Answer</summary>

`mypy` and `ruff` check the code they see, so they will notice type and style problems in `cart.py`. pytest will not notice missing tests, because pytest only runs tests that exist. Coverage tools (pytest-cov) can report untested lines, and **code review** is the safety net: the checklist in section 16.4 asks "Is it tested?".

</details>

**Try it.** Build `pricekit` yourself, from an empty folder, without copying. Then (1) add a function `bulk_price(price, quantity)` on a branch `add-bulk-price`, with tests, a docstring, a CHANGELOG entry under `Unreleased` and a commit message that explains why; (2) merge it with `--no-ff`; (3) release `0.2.0`: edit the version and CHANGELOG, commit, tag `v0.2.0`; (4) make `python tasks.py check` pass from a fresh clone.

## 18. The new-project checklist

Use this list every time you start a project. Copy it into your notes.

**Repository**
- [ ] `git init`, default branch `main`, identity set
- [ ] `.gitignore` (Python, venv, caches, `.env`)
- [ ] `LICENSE`
- [ ] first commit is housekeeping only

**Layout**
- [ ] `src/<package>/` with `__init__.py`, `py.typed`
- [ ] `tests/` mirroring the package
- [ ] one `pyproject.toml`: metadata, `dev` extra, pytest, ruff, mypy
- [ ] version in one place only

**Tasks**
- [ ] `tasks.py` (and/or `Makefile`) with `test`, `lint`, `types`, `fmt`, `check`, `clean`
- [ ] helpful message when a tool is missing

**Docs**
- [ ] README answers: what, example, install, use, develop, license
- [ ] docstrings with an example on public functions
- [ ] `CHANGELOG.md` with an `Unreleased` section

**Automation**
- [ ] `.pre-commit-config.yaml`
- [ ] CI runs the same `check` command as you do locally
- [ ] branch protection on `main` once you use GitHub

**Habits**
- [ ] one branch per task, small commits, imperative messages
- [ ] self-review your diff before every PR
- [ ] fresh clone test before every release

## 19. Common traps

Collected from the whole chapter. Read them before a real project.

**Git history and commits**
1. **Giant commits** ("many changes"). Impossible to review or revert. One purpose per commit.
2. **Committing secrets.** Ignoring a file later does not remove it from history. Revoke the key.
3. **`.gitignore` after the fact.** It does not affect tracked files; use `git rm --cached`.
4. **Committing generated files** (`__pycache__`, `.venv`, `dist`).
5. **Vague messages** (`fix`, `update`, `asdf`). Say what and why, in the imperative.

**Branches, merges, rebases**
6. **Merging the wrong way round.** `git merge x` merges `x` *into the branch you stand on*. Check `git branch` first.
7. **Leaving conflict markers** (`<<<<<<<`) in a file and committing. Search with `git grep`, and run the tests.
8. **Rebasing shared history.** Never rewrite commits other people have.
9. **Plain `git push --force`.** Use `--force-with-lease`. Never force `main`.
10. **Long-lived branches** lead to huge conflicts. Merge or rebase often.
11. **Ours/theirs swapped in a rebase.** Read the marker labels.
12. **Branch not deleted after squash**: `git branch -d` says "not merged". The squash made a new commit; check the content, then `-D`.

**Undoing**
13. **`git restore` / `reset --hard` destroy uncommitted work** with no way back. Commit or stash first.
14. **Using `reset` on pushed commits.** Use `revert`.
15. **Panic after `reset --hard`.** Committed work is in `git reflog` for weeks.
16. **Committing in a detached HEAD** and then switching away. Read git's warning; make a branch.
17. **`git clean -f` without `-n`.** Dry-run first.

**Remotes**
18. **Pushing before pulling** gets rejected. `git pull --rebase`, then push.
19. **Wrong identity** (company email on personal projects, or the reverse). Check `git config user.email` per repository.
20. **Hooks live in `.git/hooks`** and are not shared. Use the pre-commit framework.

**Project and tools**
21. **Flat layout hides packaging bugs**: tests import the folder, not the installed package. Use `src/`.
22. **Spaces instead of a TAB in a Makefile**: `missing separator`.
23. **Forgetting `.PHONY`**: a file named `test` stops `make test`.
24. **Calling bare `pytest`/`pip`** from the wrong environment. Use `python -m pytest`, `python -m pip`.
25. **Dev tools in `dependencies`.** Users should not need pytest. Use the `dev` extra.
26. **Two sources of truth** (version in two files, checks in CI that differ from local). Keep one.
27. **A README that was never tested** on a clean machine.
28. **CI that runs different commands** from the local ones. CI should run `check`.
29. **Taking review personally**, or reviewing with "this is wrong" and no reason.
30. **Huge pull requests.** Nobody can really review them.

## 20. Summary

- A **commit** is a snapshot with a parent pointer; history is a **graph**. A **branch** is a movable label; `HEAD` is "where you are". Files live in three places: working tree, **index**, repository, and `add` / `commit` move changes between them.
- Make **small, focused commits** with imperative messages that explain *why*. Keep junk and secrets out with `.gitignore`.
- **Merge** joins lines of work and records it. A **conflict** only means "decide"; edit the file, remove the markers, `add`, `commit`, then test. `merge --abort` is always available.
- **Rebase** replays commits for a straight history; **interactive rebase** (`pick`, `reword`, `squash`, `fixup`, `drop`) cleans your *own* local commits. Never rewrite shared history.
- **Undo** by situation: `restore` for files, `amend` for the last commit, `reset` for unpushed commits, `revert` for pushed ones, **`reflog`** to recover. `stash` and `cherry-pick` are small, precise tools; `bisect`, `blame` and `log -S` find where problems came from.
- **GitHub flow**: branch from `main`, push, open a PR, review, CI, merge, delete the branch. Use `--force-with-lease`, never force `main`.
- A professional Python project has the `src` layout, one `pyproject.toml` (metadata and tool settings), tests, ruff, mypy, a **task runner** with the same names everywhere (`tasks.py` for any OS, `make` where available), hooks, CI that runs the same command, a README that works for a stranger, docstrings, a CHANGELOG and semantic versions.
- **Review** is a conversation about code: small PRs, self-review first, specific kind comments with a label, and replies to every comment.
- The **`pricekit` template** collects all of this. Copy it for every project and run the checklist.

You now have the habits that make every later module in this course easier to build, share and trust.

