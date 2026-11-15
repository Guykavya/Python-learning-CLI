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

The syllabus has **92 modules, and every one of them has its chapter** (about 250,000 lines of
book-style text with worked examples, common traps and summaries). **Problems** with automatic
tests are written module by module and exist today for the first part of the path:

| Track | Modules | Chapters | Modules with problems | Problems written / planned |
|---|---|---|---|---|
| Core Python | 24 | 24 | 24 | 1,075 / 1,075 |
| Shared (SQL, data pipelines) | 2 | 2 | 2 | 105 / 105 |
| DSA | 18 | 18 | 7 | 310 / 785 |
| Software engineer | 11 | 11 | 0 | 0 / 375 |
| Data analyst | 13 | 13 | 0 | 0 / 510 |
| Data scientist | 10 | 10 | 0 | 0 / 400 |
| AI/ML engineer (deep learning) | 7 | 7 | 0 | 0 / 220 |
| AI/ML engineer (LLM applications) | 7 | 7 | 0 | 0 / 185 |

A module that has a chapter but no problems yet shows **"chapter ready"** in `learn syllabus`:
you can read it with `learn read <module>`, and nothing is locked. Each track also has a
**capstone guide** in `docs/guides/` (a project checklist with a review process). Run
`./learn syllabus` for the live numbers. New problems are added one module at a time.

## Install

You need **Python 3.11 or newer** (any newer version works). Git is optional: it only
makes downloading easier and lets `learn` keep a private history of your progress.
Internet is needed once, to install the packages the engine uses (PyYAML, pytest, Pygments, Rich, and tzdata on Windows).

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

### Extra packages (large downloads)

The base install covers most modules. Install an extra only when you reach it, then check with `learn doctor <module>`.

| Extra | Command | Needed by |
|---|---|---|
| `ml` | `.venv/bin/python -m pip install -e ".[ml]"` | ds.04, ml.01 to ml.07 (torch, transformers, xgboost, mlflow, dvc, onnx; several GB) |
| `llm` | `.venv/bin/python -m pip install -e ".[llm]"` | llm.03 (PDF reading) |
| `providers` | `.venv/bin/python -m pip install -e ".[providers]"` | Optional: only if you later connect a real Anthropic or OpenAI key. The llm chapters run offline without it. |

On Windows use `.venv\Scripts\python.exe` instead of `.venv/bin/python`.

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
| `learn reset` | Start over: saves a backup zip in `backups/`, then erases your progress and solutions (`--all` also erases `config.toml`, `playground/` and `library/`) |
| `learn doctor [module]` | Which packages a chapter needs and whether they are installed (`--all`, `--strict`) |
| `learn extract <module>` | Save the files a chapter builds (projects, tests) into `library/` to open in your editor |
| `learn verify <module>` | Run every code block of a chapter and compare with the printed output (`--strict-encoding`) |
| `learn lint` | Check every chapter is well formed (`--fix-encoding`, `--strict`) |
| `learn cards [module]` | Export Q&A and predict-the-output boxes as flashcards (CSV or Anki) |
| `learn capstone <track>` | Open the capstone guide of a track |
| `learn new <module> "<title>"` / `learn validate` | Write your own problems |

### Windows

Use `learn.cmd` (the launcher sets UTF-8 for you). If you run Python yourself, set `PYTHONUTF8=1`, or
accented text and emoji in chapters can fail with cp1252 errors. `learn doctor` warns about this.
CI runs the engine tests on Linux, macOS and Windows.

**Reading chapters.** `learn read` draws the chapter as formatted Markdown (tables, quotes, coloured code) with the
Rich package, which is pure Python and installs with the course on every system. On Linux and macOS a long section
pages through `less` (Space: next page, `b`: back, `q`: stop). Windows has no `less`, so a long section prints in one go
and you scroll up with the mouse wheel or Shift+PageUp. Use Windows Terminal (the default on Windows 11) or VS Code's
terminal for colours; the old `cmd.exe` window can show raw colour codes. If Rich is missing, the reader quietly falls
back to a simpler line-by-line style; `.venv/bin/python -m pip install -e .` (Windows: `.venv\Scripts\python.exe`) restores it.

**Full-screen mode (optional).** One setting turns the whole course full-screen:

```
./learn config set ui.mode tui
```

Install the extra package once (Windows: `.venv\Scripts\python.exe` instead of `.venv/bin/python`):
`.venv/bin/python -m pip install -e ".[tui]"`. With `ui.mode = tui`, the same commands open full-screen screens:

| You type | You get |
|---|---|
| `learn` | **Home**: today's plan, where you are in each track, and keys: `c` continue, `n` next problem, `r` read, `s` syllabus, `t` stats, `i` problem by id, `q` quit |
| `learn start <id>`, `learn next`, `learn work` | **Problem workspace**: the statement on the left; tabs on the right for your file, hints, the last check and the walkthrough. Keys: `c` check, `h` hint, `s` solution (asks first until solved), `x` stuck prompt, `e` open in VS Code, `f` back to your file, `q` quit |
| `learn syllabus [track]` | **Syllabus browser**: tracks and modules with progress. Keys: `r` read the chapter, `p` jump to the problems (Enter opens one), `m` back to the modules, `g` make this the current module, `q` quit |
| `learn read <id>` | **Chapter reader**: contents on the left, the section on the right. Keys: `n`/`p` next and previous, `a` answers, `c` hide the contents, `q` quit |

Notes:

- You still write code in your own editor. The workspace's "My file" tab only shows the file and updates each time you
  save (turn on auto-save in VS Code). Scoring is identical in both modes, because the workspace runs the same code as
  `learn check`, `learn hint` and `learn solution`.
- The home screen is alive: a shimmering PYTHON logo, a clock with a time-of-day greeting in the top-right corner, slow
  code rain in the empty areas, and the Zen of Python typed out line by line on the right (it starts at `>>> import this`,
  each line appears below the previous one, and when all 19 are done it wipes and starts again). Your name comes from
  `learn config set ui.name "Your Name"` (empty = no name shown). `learn config set ui.animations false` gives a still
  screen. Press **Ctrl+P**, type `theme`, and pick "Change theme" to try colour themes (Nord, Gruvbox, Dracula...).
  On a narrow terminal (under 120 columns) the poem is hidden to leave room for the plan.
- `learn check`, `hint`, `solution`, `stats`, `today` and the authoring commands stay plain text, so they work in pipes and scripts.
- Anything that is not a real terminal (a pipe, a script, CI) is always plain. Without Textual installed, `learn` says so
  once and stays plain. For one run in the other mode: `learn --plain ...`, or `LEARN_UI=tui learn ...`.
- `learn read <id> --tui` and `learn work <id>` open those screens for one run even when the mode is `plain`.
- On Windows use Windows Terminal (the default on Windows 11) or VS Code's terminal. The old `cmd.exe` window can draw
  full-screen apps badly.

### Guides and cheat sheets

- [Study roadmap and daily routine](docs/guides/study-roadmap.md)
- [Turning capstones into a portfolio](docs/guides/portfolio.md)
- Cheat sheets in `docs/reference/`: [Python](docs/reference/cheatsheet-python.md), [SQL](docs/reference/cheatsheet-sql.md), [NumPy and pandas](docs/reference/cheatsheet-numpy-pandas.md), [Git, shell, Docker](docs/reference/cheatsheet-git-shell-docker.md), [glossary](docs/reference/glossary.md)

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
