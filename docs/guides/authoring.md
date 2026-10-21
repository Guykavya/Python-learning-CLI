# Writing your own problems

The module keeps growing without any AI if you add problems yourself.
Writing a good problem with tests is itself one of the best ways to learn a topic.

## Create one

```bash
learn new core.05 "Remove duplicates keeping order" --tier applied --kind code
```

This creates `content/core/<module folder>/problems/pNNN-<slug>/` with every file filled
with a template. Edit them, then run:

```bash
learn validate core.05
```

Validation checks that every file exists, that there are at least two hints,
that `reference.py` passes the tests, and that `starter.py` does **not** pass them.

## The three kinds

| Kind | You write | The learner writes | Checked by |
|---|---|---|---|
| `code` | `starter.py`, `test_solution.py`, `reference.py` | `solution.py` | pytest |
| `trace` | the code inside `problem.md`, and `expected.txt` | `answer.txt` | exact line-by-line match |
| `explain` | `answer.md` (model answer) | `answer.md` | self-rating against the model answer |

## Files in every problem

- `problem.toml` holds the id, title, tier, kind, topics, and optional `difficulty`, `minutes` and `assessment`.
- `problem.md` holds the statement, with at least one example.
- `hints.md` holds sections `## Hint 1`, `## Hint 2`, and so on. Go from a guiding question to pseudocode.
- `solution.md` holds the walkthrough: approach, code, complexity, another way.
- `mistakes.md` holds the common mistakes and why they are wrong.

## Tiers

| Tier | Meaning |
|---|---|
| `drill` | Exercises one concept in isolation |
| `applied` | A realistic small task using the concept |
| `deep` | Explain, debug, trace or compare. Edge cases and internals |
| `challenge` | An unfamiliar combination with earlier topics |

Set `assessment = "explain" | "trace" | "fix" | "build"` on the problems that prove mastery.
Each module should have one of each.

## Writing tests that teach

Every assertion should carry a message that explains the likely mistake, for example:

```python
assert run("0\n") == ["0"], "0 has one digit, 0. Make sure your loop does not print nothing."
```

**Two test styles:**

- **Function style**, from core.06 onward. The test imports from `solution`:
  `from solution import dedupe`.
- **Script style**, for early modules before functions. The test runs `solution.py` as a
  program, feeds keyboard input, and checks printed lines. Copy the `run()` helper from
  any core.02 problem.

Data files the tests need go in a `fixtures/` folder inside the problem.

## DSA site problems

To map LeetCode, Codeforces or CSES problems into a DSA module, create
`content/dsa/<module folder>/external.toml`:

```toml
[[problem]]
site = "leetcode"
key = "two-sum"
title = "Two Sum"
url = "https://leetcode.com/problems/two-sum/"
minutes = 20
```

The daily plan then includes them, and they count as done once you sync or log them.
