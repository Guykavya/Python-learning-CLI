# Writing the remaining modules with a free AI chatbot

Use this if Claude Code (the paid tool that wrote core.01–core.15) is no longer available.
A free chatbot (claude.ai free, ChatGPT free, Gemini, etc.) cannot see your folder or write
files. It only produces text. So **you** are the hands: you copy its output into files and
run `./learn validate`. This guide makes that work in small, safe pieces.

## How a free chatbot is different

| Claude Code (paid) | Free chatbot |
|---|---|
| Reads your files, writes files, runs tests | Only chats. You paste text in and out |
| Can write 2,800 lines in one go (with helpers) | Cuts off after roughly 300–600 lines per reply |
| Remembers the whole project | Forgets between chats, and gets confused in long ones |
| Hundreds of messages | A small daily message limit, which resets later |

So the rules are:

1. **One small piece per message.** One chapter part, or 3–5 problems. Never "write all of core.16".
2. **A new chat for each module** (long chats get worse). Start it with the Setup Prompt below.
3. **Always say "continue" when it stops mid-way**, then paste the rest into the same file.
4. **Never trust it blindly.** The chatbot cannot run code. `./learn validate` is the judge.
5. If you hit the daily limit, stop, and carry on tomorrow. Nothing is lost: every finished piece is already a file.

## The order of work for ONE module (example: core.16)

Do these steps in order. Each step is one message to the chatbot.

### Step 0. Get the plan (no AI needed)

```bash
cd "<project folder>"
grep -n -A22 "id: core.16$" syllabus.yaml      # topics, outcomes, problem count, project
ls content/core/core.15-*/problems | head -5   # see the folder naming
```

### Step 1. Setup Prompt (paste this first, in a NEW chat)

Fill the `<...>` parts. Paste the syllabus entry you got from the grep.

```text
I am building an offline Python course. I write the files; you only produce text.
Module: <core.16 Advanced typing>. Syllabus entry:
<paste the grep output>

Rules for everything you write:
- Simple, clear English. "Why" before "how". Worked examples. Common traps. Short summary.
- Python features only from earlier modules (core.01-core.15) plus this module's topics.
- Every code example must be correct for Python 3.12+. If you are not sure what some code
  prints, do not invent output: mark it "(run it to see)".
- I will ask for one small piece at a time. Reply with only that piece, no extra chat.
Reply "ready" if you understand.
```

### Step 2. Plan the problems (1 message)

```text
Plan the <35> problems for this module as a numbered list: number, short-slug, tier
(drill/applied/deep/challenge), kind (code/trace/explain). Mix: about 1/3 drill, 1/3 applied,
the rest deep and challenge. About 10 trace and 5 explain (fewer if the count is small).
Exactly one problem each with assessment explain, trace, fix, build. The last problem is
the module project: <paste the "project:" line>. One line per problem, nothing else.
```

Save the answer as `content/core/<module folder>/PLAN.md` (you can delete it later).
This list is your memory. Every later message refers to it.

### Step 3. Write the chapter in parts (about 6–8 messages)

The chapter is `chapter.md`. Ask for it in parts of roughly 300 lines each:

```text
Write chapter part 1: sections "## 1." to "## 3." covering <first topics>.
Format rules: "## N. Title" for main sections, "### " for subsections.
For "Try it" exercises put the answer inside:
<details><summary>Answer</summary>
...answer...
</details>
(opening tag on one line, closing tag on its own line).
```

Then: "Part 2: sections 4 to 6 ..." and so on. Append each part to `chapter.md`.
Between parts, run the code examples yourself (`python3 -c ...`) and fix any printed
output that is wrong. This is the most important quality step.

### Step 4. Write problems in batches of 3–5 (about 8–12 messages)

Show the chatbot ONE finished problem as the sample first (it must see the real format).
Open any problem folder from the previous module and paste these files into the chat:
`problem.toml`, `problem.md`, `hints.md`, `solution.md`, `mistakes.md`, `starter.py`,
`test_solution.py`, `reference.py`. Then:

```text
Here is one finished problem. Copy this exact file layout and style.
Now write problems p001, p002, p003 from the plan (below). For each one give every file,
each in its own code block headed by the file path. Rules:
- test_solution.py: every assert has a message that names the likely mistake.
- starter.py must FAIL the tests (a stub), reference.py must PASS them.
- hints.md: at least 2 hints, from a guiding question to pseudocode.
- Trace problems: put the code in problem.md and give expected.txt only after you
  trace it carefully; I will check it by running the code.
<paste the plan lines for these problems>
```

A faster way to get the file layout: let the engine make empty templates, then ask the
chatbot to fill them in:

```bash
./learn new core.16 "Short title" --tier applied --kind code
```

### Step 5. Validate after every batch (no AI needed)

```bash
ulimit -v 1000000; ./learn validate core.16 | tail -20
```

It lists only failures. For each failing problem, send the chatbot:

```text
This problem fails validation with: <paste the message>.
Here are test_solution.py and reference.py: <paste both>.
Decide whether the test or the reference is wrong according to problem.md, and fix only that.
```

Check the problem statement yourself before accepting the fix. A wrong test is worse than
a missing problem. Trace problems: run the code and compare it with `expected.txt` yourself.

### Step 6. Done when

- `./learn validate core.16` says all problems valid.
- The count equals `problems:` in `syllabus.yaml`.
- Exactly one problem each with assessment explain, trace, fix, build.

## If you run out of messages mid-module

You can always stop with a half-finished module: the course already works without the rest.
Validated problems are usable at once. Mark progress in `PLAN.md` ("done up to p018") so
the next chat knows where to continue. Quality over quantity: 20 good problems beat 35 shaky ones.
You may also lower `problems:` for that module in `syllabus.yaml`.

## Order of the remaining core modules

| Module | Title | Problems | Needs |
|---|---|---|---|
| core.15 | Python data model essentials | 55 | core.14 |
| core.16 | Advanced typing | 35 | core.09, core.14 |
| core.17 | Standard library deep tour | 60 | core.12 |
| core.18 | Regular expressions and text processing | 45 | core.03, core.07 |
| core.19 | Advanced testing | 40 | core.08, core.14 |
| core.20 | Debugging, profiling and code quality | 30 | core.19 |
| core.21 | Concurrency and parallelism | 50 | core.17, core.14 |
| core.22 | Pythonic design and patterns | 30 | core.15, core.19 |
| core.23 | Attribute machinery and metaprogramming | 35 | core.15 |
| core.24 | CPython internals | 35 | core.23, core.21 |

Do them in this order. Skip a module you do not need yet; the DSA modules (dsa.02 onward)
do not depend on them, so you can switch to DSA content when core feels like too much.
The same method works for DSA, shared, swe, da, ds and ml modules.

## Tips that save messages

- Ask for **several small files in one reply**, not one file per reply.
- When something is wrong, paste only the failing file and the error, not the whole chat.
- Machine with little RAM: always `ulimit -v 1000000` before running validation or odd code.
- Prefer a chatbot that can run code (some free tools offer a code sandbox): ask it to run the
  tests before giving you the answer.
- Keep each chat short. New chat, Setup Prompt again, and the plan lines you still need.
