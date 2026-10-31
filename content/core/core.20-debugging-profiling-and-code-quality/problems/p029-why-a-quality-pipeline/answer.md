## The five lines

1. **`import os` unused: ruff (F401).** Static analysis sees the name is never read. mypy and
   tests do not care: unused code runs fine.
2. **`len(values)` can be 0: none of the static tools.** The types are correct (`list[int]` in,
   `float` out); `average([])` raises `ZeroDivisionError` at run time. Only a **test** with an empty
   list (an edge-case test) finds it.
3. **`age: int = find(...)`: mypy.** `find` returns `Optional[int]`, so `age` may be `None` and
   `age >= 18` would crash. In `--strict` mode mypy also complains that `describe` has no
   annotations. Tests catch it only if one passes a missing name.
4. **Bare `except:`: ruff (E722).** It also swallows `KeyboardInterrupt` and hides the `None`
   bug from line 3 behind "unknown". Tests pass, which is exactly the danger.
5. **`sum(prices)*1.18`: ruff format** rewrites it to `sum(prices) * 1.18` (layout only). The
   real bug, **floats for money** (rounding errors), is found by no tool; only a test with
   exact expected amounts, or a code review, notices it.

## What each tool is for

- **ruff check**: fast pattern rules (unused names, bare except, mutable defaults, outdated
  syntax, import order). Runs in milliseconds, can auto-fix many. Misses anything that needs
  types or running the code.
- **ruff format / black**: makes layout identical for everyone, so diffs show real changes and
  reviews stop arguing about spaces. Finds no bugs at all.
- **mypy**: checks that values flow through the code with the right types: `None` where a value
  is required, wrong return types, missing attributes. Covers every path, even ones no test
  runs. Misses wrong values of the right type (`0` length, wrong formula) and anything in
  unannotated code (unless `--strict` forces annotations).
- **pytest**: the only one that checks **behaviour**: right answers, edge cases, exceptions,
  integration with files and other parts. Misses paths nobody wrote a test for (coverage shows
  where) and says nothing about style or types on untested paths.

## Why this order

Fixers first because they **change** the files: ruff `--fix` may remove an import, then the
formatter settles the layout, so everything after them checks the final text. mypy is
read-only and takes seconds, still fine per commit. The test suite can take minutes and needs
the whole project, so it runs on the CI server on every push (developers still run the relevant
tests locally). Cheap, fast checks run often; expensive ones run less often but always before
merging.

## Cost and how to keep it low

Each commit waits for the hooks (ruff: milliseconds, mypy: seconds with its cache). Strict rules
produce some false alarms that need a `# noqa` or a config exception, and adopting mypy on old
code means a burst of annotation work. Teams keep the cost low by pinning tool versions
(`rev`), enabling rules gradually, using `per-file-ignores` instead of blanket ignores, running
only on changed files, and keeping slow tests out of pre-commit.

**To the teammate:** the tests only prove what they test; the static tools check every line in
milliseconds, catching whole classes of bugs (like line 3) before a test ever runs, and they
cost almost nothing per commit. Each tool sees different problems, so together they miss far
less than any one of them.
