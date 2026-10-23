# Python Learning Module

Learn Python offline, with tests that explain your mistakes and reviews that make it stick.
It runs in your terminal and needs no AI. After a one-time install it needs no internet
either, except to sync LeetCode and Codeforces solves.

- **Learn:** book-style chapters in simple English. Each explains why before how, with worked examples and common traps.
- **Practise:** problems with automatic tests, hints that go from a question to pseudocode, and
  predict-the-output, explain-in-words and fix-the-bug exercises. A failing test names the likely mistake.
- **Retain:** problems come back on a growing review schedule. The tracker shows your weak
  topics and only counts a module as mastered when you really can solve it.

The plan is a long path: Python from the first program to CPython internals, then four
career tracks (software engineer, data analyst, data scientist, AI/ML engineer), with
data structures and algorithms alongside.

## What exists today

The syllabus has 92 modules. **12 are written so far**, with over 500 tested problems:

| Track | Written | Planned |
|---|---|---|
| Core Python | 10 of 24 modules (basics, strings, control flow, collections, functions, errors, testing, type hints, generators) | the rest of the language, standard library, concurrency, internals |
| DSA | 2 of 18 modules (problem-solving basics, complexity) | arrays through dynamic programming |
| Software engineer, data analyst, data scientist, AI/ML | none yet | planned |

Unwritten modules show as "not written yet" in `learn syllabus`, and nothing is locked. Run
`./learn syllabus` for the live numbers. New modules are added one at a time.

## Install

You need **Python 3.11 or newer** (any newer version works). Git is optional: it only
makes downloading easier and lets `learn` keep a private history of your progress.
Internet is needed once, to install the three packages the engine uses (PyYAML, pytest, Pygments).

**1. Get the project.** Either clone it:

```
git clone https://github.com/Guykavya/Python-learning-CLI.git
cd Python-learning-CLI
```

or, without Git, click the green **Code** button on
[the GitHub page](https://github.com/Guykavya/Python-learning-CLI), choose **Download ZIP**,
extract it, and open a terminal in the extracted folder.

**2. Run it.** The first run builds a private environment in `.venv/`. It takes a minute, once.

| Where | Command |
|---|---|
| Windows PowerShell | `.\learn.cmd init` |
| Windows CMD | `learn.cmd init` |
| Linux / macOS | `./learn init` |

Then, on Windows, type `.\learn.cmd` (PowerShell) or `learn.cmd` (CMD) wherever this page
says `./learn`.

**No Python yet, or too old?** The launcher tells you. To install it:

- Windows: `winget install Python.Python.3.13`, or download it from [python.org](https://www.python.org/downloads/)
  and tick **Add python.exe to PATH**. Open a new terminal afterwards.
- Ubuntu / Debian: `sudo apt install python3 python3-venv`
- macOS: download from [python.org](https://www.python.org/downloads/) or `brew install python`

**Something went wrong?** Delete the `.venv` folder and run the command again; the launcher
rebuilds it. To pick a specific Python, set `LEARN_PYTHON` to its path first
(PowerShell: `$env:LEARN_PYTHON = "C:\path\to\python.exe"`, Linux/macOS: `LEARN_PYTHON=/path/to/python3 ./learn init`).

### Optional settings

Your settings live in `config.toml`, created on first use. To sync your online solves
and set your daily study time:

```bash
./learn config set accounts.leetcode_username <your-name>
./learn config set accounts.codeforces_handle <your-handle>
./learn config set plan.daily_minutes 90
```

`config.example.toml` shows every setting with comments.

## Start here

```bash
./learn              # menu: today's plan plus numbered choices
./learn today        # what to do today
./learn next         # start the first item
./learn check        # test your work
```

Inside a VS Code terminal with the `.venv` environment active, plain `learn` works too.
Press Tab to complete commands and problem ids (`learn completion` shows the one-time setup).

## How a session goes

1. `learn today` shows reviews that are due, new problems from your current modules, and a DSA item.
2. `learn next` (or `learn start <id>`) puts the problem in `my-work/` and prints it.
3. Write your answer in the file it names. Open the folder in VS Code.
4. `learn check` runs the tests. A failing test tells you what went wrong.
5. Stuck? `learn hint` reveals one hint at a time. After a real attempt, `learn solution` shows the walkthrough.
6. Still stuck? `learn stuck` writes a ready-made prompt you can paste into any free chatbot.

Each solve is scored for quality (hints, failed checks and solution views lower it).
Problems come back for review on a growing schedule, solved from a blank file each time.

## Your progress is private

Everything that is yours stays on your computer and out of the course repository:
`my-work/`, `data/progress.db`, `config.toml`, and anything you put in `playground/` or `library/`.

After every solve, `learn` saves these to a separate Git history in `.progress.git/`,
so your work is never lost. To look at it:

```bash
git --git-dir=.progress.git log --oneline
```

Back up that folder (or the whole project folder) if you move to a new computer.

## Getting new modules

New chapters and problems are added over time. To get them:

```bash
git pull
```

Your progress is untouched, because none of it is part of the course repository.
`learn syllabus` shows which modules have content.

## Commands

| Command | What it does |
|---|---|
| `learn today` / `learn next` | Today's plan / start its first item |
| `learn start <id or number>` | Start a problem; `--review` re-solves a solved one; `--code` opens VS Code |
| `learn check` / `hint` / `solution` / `stuck` | Work on the current problem |
| `learn resume` | Where you stopped, with a warm-up after long breaks |
| `learn syllabus [track]` | Every module with progress (`★` mastered, `◐` in progress) |
| `learn module <id>` | Topics, outcomes, project and problems of one module |
| `learn read <module>` | Read the chapter here, section by section; it remembers where you stopped (`--restart`, `--code` for VS Code) |
| `learn goto <module>` / `learn goto <track> --auto` | Jump anywhere; nothing is locked |
| `learn focus core dsa swe` | Choose which tracks feed the daily plan |
| `learn review` | Reviews due now and this week |
| `learn stats` / `stats dsa` / `stats topics` | Progress, DSA by pattern, weakest topics |
| `learn log lc <slug>` / `log cf 1520A` / `log cses 1068` | Record an outside solve and save its code |
| `learn sync` | Pull solves from Codeforces and LeetCode |
| `learn config show` / `config set plan.daily_minutes 120` | Settings |
| `learn new <module> "<title>"` / `learn validate` | Write your own problems |

## Folders

| Folder | Purpose |
|---|---|
| `syllabus.yaml` | All tracks and modules with topics, outcomes and prerequisites |
| `content/` | Chapters and problems, organised as track/module/problems |
| `my-work/` | Your solutions, managed by `learn`. Reviews go into `reviews/<date>/` *(private)* |
| `playground/` | Your free zone. Nothing is graded; `learn` notices what you practise *(private)* |
| `library/` | Your books and notes *(private)* |
| `data/progress.db` | The tracker (SQLite). Open it with the SQLite Viewer extension *(private)* |
| `docs/guides/` | How-to guides: DSA syncing, writing problems |
| `engine/` | The `learn` program itself, with its own tests (`.venv/bin/python -m pytest`) |

## Mastery

A module is mastered when you have solved at least 70% of its problems,
your average quality is at least 0.7, and you have passed its assessment problems
(explain, trace, fix, build). Problem counts alone do not count as mastery.

## Branches

- `master`: the stable course. Clone and pull from this one.
- `dev`: modules still being written. It may be incomplete or broken.

## Writing your own content

Everything above runs on plain Python and SQLite. To add your own problems or modules,
see `docs/guides/authoring.md`.

## Licence

- **The program** (`engine/`, `learn`, `learn.cmd`) is under the [MIT licence](LICENSE).
- **The course** (`content/`, `syllabus.yaml`, `docs/`, this README) is under
  [Creative Commons BY-NC-SA 4.0](LICENSE-CONTENT): you may share and adapt it with credit,
  but not for commercial use, and your changes must use the same licence.
