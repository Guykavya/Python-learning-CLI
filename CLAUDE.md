# Instructions for Claude in this project

This is Kavya's offline Python mastery system: a CLI engine (`./learn`), a SQLite tracker,
and book-style content (chapters + tested problems) for the modules in `syllabus.yaml`.
It must work with **no AI** once the subscription ends, so all quality lives in the content.

## Two roles — know which one you are in

- **Tutor** (Kavya is solving problems in `my-work/`): never give a full solution before a real
  attempt. Ask guiding questions, point at the failing test message, nudge toward the next hint.
- **Author** (Kavya asks for new modules/content): follow the workflow below.

Never touch `my-work/` or `data/progress.db` unless asked. The only remote allowed is Kavya's
personal GitHub (never a company account or company remote).

## Publishing and branches

- `master` is the stable public course; `dev` is where modules are written. Author on `dev`.
- Personal files (`my-work/`, `data/`, `config.toml`, `playground/`, `library/`) are gitignored.
  `learn` snapshots them into a separate private history, `.progress.git/` (see `engine/learn/gitsnap.py`).
- New settings go into `config.example.toml` too, with empty personal values.

## Authoring workflow — ONE module per session

Writing content is expensive in tokens. Build exactly one module per request, then stop
and report. Do not start the next module unless Kavya asks.

1. Find the next module: `ls content/core content/dsa`, then compare with
   `grep -n "      - id:" syllabus.yaml`. Read **only** that module's syllabus entry
   (`grep -n -A22 "id: core.NN$" syllabus.yaml`): topics, outcomes, `problems:` count, project.
2. Read `docs/guides/authoring.md` (short) and **one** problem of each kind from the previous
   module as the format sample. Do not read whole earlier chapters or many problems.
3. Write `chapter.md`, then the problems, in `content/<track>/<id>-<slug>/`.
   Prefer one subagent per module (chapter + problems) so file contents stay out of the main
   context. Do not run several modules in parallel.
4. Run `./learn validate <id>`. Only open the problems that fail. Fix the tests or the
   reference — check which one is wrong against the problem statement before changing anything.
5. Report: problem count, tier/kind mix, validation result. Update the status in memory.

## Content rules

- Chapter: book-style and deep, simple, clear English, worked
  examples, "why" before "how", common traps, a short summary. Earlier chapters run 1,600–2,800 lines.
- Chapter structure: `## N. Title` main sections (the terminal reader pages by `## `), `### ` subsections.
  "Predict the output" / "Try it" answers go in `<details><summary>Answer</summary>` … `</details>`
  (opening tag on one line, closing tag on its own line): the reader hides them until the learner presses `a`.
  Example output must come from actually running the code; label machine-specific values (addresses, ids).
- Problem count = `problems:` in the syllabus. Rough mix: ~1/3 drill, ~1/3 applied, rest deep +
  challenge. Mostly `code`, plus ~10 `trace` and ~5 `explain`.
- Exactly one problem each with `assessment = "explain" | "trace" | "fix" | "build"`.
- Every problem: `problem.toml`, `problem.md` (with an example), `hints.md` (≥2 hints, question →
  pseudocode), `solution.md` (approach, code, complexity, another way), `mistakes.md`.
- Tests teach: every assert has a message naming the likely mistake.
  Before core.06: script style (`run()` helper, stdin → printed lines).
  From core.06 on: function style (`from solution import f`).
- Only use Python features taught in this module or earlier ones.
- Hand-trace any test that walks through steps (grids, turns, loops). core.04.p058 shipped with
  wrong expected output because the trace was not checked.
- DSA modules with `external: true` also get `external.toml` (see `docs/guides/dsa-sync-guide.md`).

## Token savers

- Don't re-read files already summarised in this file or in memory.
- Use `grep`/`sed -n` for slices of `syllabus.yaml` (1,600 lines) — never read it whole.
- Read `learn validate` output with `tail`; it lists only the failures.
