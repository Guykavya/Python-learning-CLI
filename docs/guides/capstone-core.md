# Core capstone: a full-featured CLI application

You have finished (or nearly finished) the Core track. The capstone proves you can
combine it. You choose the idea, design it, build it and ship it. Nobody gives you a
solution. The checklist at the bottom is how you (or a reviewer) decide it is done.

Syllabus line: *Full-featured CLI application (packaged, typed, tested, documented).*

## Rules

- **It is yours.** Your idea, your design, your code. Use the course chapters and the
  official docs, not generated code. A reviewer (a friend, or Claude in tutor mode)
  reads and comments; they do not rewrite it.
- **Own folder, own repo.** Keep it outside `my-work/`, with its own git history on your
  personal GitHub. Never a company account or company remote.
- **Offline-friendly.** Standard library plus a few well-chosen packages. Anything you
  install must be listed in `pyproject.toml`.
- **Size.** About 800–2,500 lines of code, plus tests. Smaller than that and it is a
  script; much bigger and you will never finish.
- **Time-box.** Plan 2–4 weeks of part-time work. Write the design note first (below).

## Pick an idea

Choose something you would really use. It needs **persistent data, several commands and
real rules**, otherwise it is a toy. Examples:

| Idea | Why it works |
|---|---|
| Expense tracker (`add`, `list`, `report`, `export`) | Money maths, dates, grouping, CSV |
| Habit / study logger with streaks and weekly summaries | Dates, files or SQLite, reports |
| Personal notes with tags and full-text search | Files, regex, indexing |
| Log analyser for a format you invent or already have | Regex, generators, big files |
| Flashcards with spaced repetition | Scheduling logic, state, SQLite |
| Task runner / mini `make` with dependencies | Graphs, subprocess, errors |
| Inventory or library manager | OOP, validation, SQLite |

If you cannot decide in a day, take the expense tracker: the domain is familiar, so all
your effort goes into engineering.

## Step 0: the design note (1 page, before any code)

Write `DESIGN.md` and keep it in the repo:

1. One-sentence purpose and who uses it.
2. The commands, with an example run of each (the exact terminal text you want).
3. The data model: what you store, where, and the file or table format.
4. The modules you will split it into and what each owns (parsing, storage, rules, output).
5. What can go wrong (bad input, missing file, corrupt data) and what the user sees.
6. What you are deliberately *not* building.

Bring `DESIGN.md` to the reviewer before you write much code. Changing a design is cheap;
changing 2,000 lines is not.

## Requirements

The checklist below is grouped by what Core taught. Tick every **Must**. Aim for most
**Should** items. **Stretch** is optional.

### A. Behaviour

- **Must:** at least 4 commands with sub-command style (`app add`, `app list`, ...) built
  with `argparse` (or another library you can justify in `DESIGN.md`).
- **Must:** data survives between runs (file, JSON, CSV or SQLite).
- **Must:** `--help` for the app and every command, with real descriptions and examples.
- **Must:** bad input gives a short human message and a non-zero exit code, never a traceback.
- **Should:** one command that produces a report or summary (grouping, totals, dates).
- **Should:** machine-readable output option (`--json`) next to the human one.
- **Stretch:** import/export, config file, colour output that switches off when piped.

### B. Code quality

- **Must:** a package layout (`src/yourapp/` with `__init__.py`, `__main__.py`), not one big file.
- **Must:** separation: parsing and printing live apart from the rules and storage, so the
  rules can be tested without the terminal.
- **Must:** type hints on every function signature; `mypy` (or your checker) is clean, or
  each ignore has a comment explaining why.
- **Must:** your own exception classes for domain errors, caught in one place at the edge.
- **Should:** at least one dataclass or enum modelling the domain instead of loose dicts.
- **Should:** context managers for files/connections; no bare `except:`; no mutable defaults.
- **Should:** `ruff` (or flake8) and a formatter are clean.
- **Stretch:** a Protocol or small abstract base for storage so you can swap file for SQLite.

### C. Tests

- **Must:** `pytest` suite that runs with one command and passes.
- **Must:** tests for the rules/logic, including at least 5 edge cases (empty data, huge
  values, duplicates, wrong types, boundary dates or amounts).
- **Must:** tests for the CLI itself (call `main([...])`, capture output and exit code).
- **Should:** use `tmp_path` and fixtures so tests never touch real user data.
- **Should:** parametrised tests for input validation.
- **Should:** coverage measured and above 80% on the logic modules, with the gaps explained.
- **Stretch:** a property-based test (hypothesis) for one rule, and one mutation check:
  break the rule on purpose and confirm a test fails.

### D. Packaging

- **Must:** `pyproject.toml` with name, version, Python requirement, dependencies and a
  console script entry point, so `pip install -e .` gives you a real command.
- **Must:** it installs and runs in a **fresh** virtual environment (try it).
- **Should:** version stored in one place; a `CHANGELOG.md` with at least one entry.
- **Stretch:** build a wheel (`python -m build`) and install that wheel in another venv.

### E. Documentation

- **Must:** `README.md` with: what it is, install steps, a 5-minute quick start, every
  command with an example, and where the data lives.
- **Must:** `DESIGN.md` updated to match what you actually built (note what changed and why).
- **Should:** docstrings on public functions and classes (explain *why*, not just *what*).
- **Should:** a "Known limits" section: honest list of what it does not do.
- **Stretch:** a short "How to contribute / run the tests" section.

### F. Engineering habits

- **Must:** git history with many small commits with clear messages (not one giant commit).
- **Must:** no secrets, no real personal data, no machine paths in the repo.
- **Should:** a `.gitignore`; data files kept out of git.
- **Should:** logging (not `print`) for diagnostics, with a `--verbose` flag.
- **Stretch:** one real use of profiling or `timeit` to justify a performance choice.

## How the review works

1. **Design review** (before coding): the reviewer reads `DESIGN.md` and asks questions.
   Typical outcomes: "this is too big, cut X" or "what happens when Y?".
2. **Midpoint check:** commands and storage working, a few tests. The reviewer runs it
   and tries to break it.
3. **Final review:** run through the checklist above. For every unticked **Must** the
   reviewer gives a pointer, not a patch ("look at how `list` handles an empty file").
4. **Fresh-machine test:** clone the repo into a new folder, create a new venv, follow
   only the README. If you get stuck, the README is the bug.

### Scoring (for yourself)

| Score | Meaning |
|---|---|
| All Musts, most Shoulds | Core capstone passed |
| All Musts only | Passed, but go back and add tests and docs polish |
| Any Must missing | Not done yet. Finish those first |

Stretch items are for pride and for your portfolio, not for the pass mark.

## Common traps

- **Starting with the code** and writing the design afterwards to match. Write it first.
- **One 600-line `main.py`.** Split by responsibility before it gets this big.
- **Tests that only call the CLI** and never check the rules directly.
- **Tests that use your real data file.** Always use `tmp_path`.
- **`print()` inside the logic.** Return values; print at the edge.
- **README written last, in 10 minutes.** Write the quick start while building; it
  doubles as your manual test script.
- **Endless scope.** When you have a new idea, add it to "Not building" in `DESIGN.md`.

## When you ask for a review

Send the reviewer: the repo path, the output of `pytest -q`, the output of your type
checker, and your own checklist with every item ticked or marked as missing. A review
that starts from your honest self-assessment is much more useful than one that starts
from nothing.
