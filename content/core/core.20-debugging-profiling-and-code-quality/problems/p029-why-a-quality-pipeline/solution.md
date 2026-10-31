## Approach

Classify problems by **where they are visible**:

| Visible in | Tool | Example here |
|---|---|---|
| layout | ruff format / black | line 5 spacing |
| syntax tree patterns | ruff check | lines 1 and 4 |
| types | mypy | line 3 |
| values at run time | pytest | line 2, the money rounding of line 5 |

No layer replaces another. The static tools are cheap and check **every** line; the tests are
expensive and check only what they exercise, but they are the only ones that know what the
right answer is.

The model answer is in `answer.md`.

## Key ideas

- A clean ruff and mypy run does not mean the code is correct (line 2).
- Passing tests do not mean the code is safe (line 4 hides a bug and the tests still pass).
- Fixers before checkers; fast before slow; everything before merge.
- The pipeline's cost is mostly paid once (setup) and then measured in seconds per commit.

## Another way

Some teams skip pre-commit and run everything only in CI. That works, but feedback arrives
minutes later and "fix lint" commits pile up. The opposite extreme, the full test suite in a
pre-commit hook, makes every commit slow, so people start using `git commit --no-verify`, and the
safety net disappears.
