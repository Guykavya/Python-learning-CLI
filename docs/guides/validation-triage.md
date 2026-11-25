# Validation triage: what to do when `./learn validate` fails

Run it as the runner does, or you will chase failures that only exist on your machine:

```bash
ulimit -v 1000000; ./learn validate <id> | tail -20      # only failures are listed
OMP_NUM_THREADS=2 MALLOC_ARENA_MAX=2 ulimit -v 1048576   # when you run pytest by hand
```

Open **only the problems that fail**. For each one, find the message in the table, then follow the section.

| `validate` says | Meaning | Go to |
|---|---|---|
| `missing <file>` | a template file was deleted or not made | 1 |
| `fewer than 2 hints` | `hints.md` needs `## Hint 1`, `## Hint 2` headings | 1 |
| `reference.py fails its own tests (a/b)` | test and reference disagree | 2 |
| `starter.py already passes the tests` | tests too weak, or starter too clever | 3 |
| a timeout (60 s) or `MemoryError` | too slow or too big | 4 |
| passes, but flaky on re-run | hidden randomness or a timing assumption | 5 |

## 1. Missing files and hints

`./learn new` makes every file. A `trace` problem needs `expected.txt`, an `explain` problem needs `answer.md`,
a `code` problem needs `starter.py`, `reference.py`, `test_solution.py`. Hint headings must be `## Hint 1`, `## Hint 2`.
An unknown `kind` or `tier` in `problem.toml` is reported too (kinds: code, trace, explain; tiers: drill, applied, deep, challenge).

## 2. The reference fails its own tests: decide which side is wrong

Do **not** edit the reference to make the test green. Work it out in this order:

1. Read the failing assert message and the pytest line (`-x -q --tb=short`).
2. Re-read `problem.md`. The statement is the contract. Decide what the *statement* says the answer is.
3. Compute the expected value **by hand or with a different method** (a slow loop, the library, a calculator).
4. Compare three things: statement, test, reference. The one that disagrees with the other two is wrong.
   - Statement and test agree, reference differs: fix the reference.
   - Statement and reference agree, test differs: fix the test (the usual case for hand-written expected numbers).
   - Test and reference agree, statement differs: fix the statement, an ambiguity or a wrong example.
5. Fix `solution.md` and `mistakes.md` if they quoted the wrong value.

Typical causes by track:

| Track | Usual cause |
|---|---|
| any | tie-break or rounding not pinned in the statement; hand-written expected value wrong (core.04.p058) |
| da / ds | pandas 3 / NumPy 2 behaviour differs from the chapter you remembered; index not reset; dtype `int64` vs `float64` compared with `==` on a list |
| da (Excel, Power BI) | test compares a value openpyxl never calculated; use formula text or the chapter's mini evaluator |
| ds / ml | exact trained number hard-coded; random stream differs across versions; threshold too tight |
| ml | `MemoryError` that is really a second heavy import (see 4) |
| llm | a scripted reply list popped in the wrong order, or the solution calls the model one time more than the test scripted |
| swe | app state shared between tests (use a factory and in-memory SQLite per test); `.html`, `.sql`, `.xlsx` files not copied to the learner (R1) |

## 3. The starter already passes

The starter must be a **stub that fails**, but still be importable. Causes:

- Stub returns `[]`, `0`, `None` and a test accepts that (empty input case with no stronger case). Add a case it cannot pass.
- Test asserts only a type or a shape. Add a value check.
- A property test is vacuous (loop over an empty list). Assert the list is not empty first.
- `pytest.approx` with a tolerance so wide a stub passes. Tighten it.

The opposite problem is **not** reported by `validate`: a starter that raises `ImportError`/`NameError`
at collection gives pytest 0 tests, and `validate` can still accept it. Define every name the test imports.

## 4. Timeout and memory

First measure, then shrink:

```bash
time pytest -q -x test_solution.py --durations=5
```

- Target: whole file about 20 s with the reference (cap 60 s, and `validate` also runs the starter).
- Shrink data (<= 5,000 rows, images <= 32x32), models (hidden <= 64, <= 2 layers), steps (<= 200), repetitions (<= 300).
- Import cost counts: pandas 1.1 s, sklearn 2.7 s, statsmodels 3.0 s, torch 3.3 s. Import heavy libraries once, in `conftest.py` or at the top.
- `MemoryError` is *virtual address space*, not RAM. If a test imports torch, it must not also import sklearn,
  scipy, pandas, mlflow or `datasets`, and the failure appears at an unrelated line such as `Adam(...)`.
  A problem has only one `test_solution.py`, so compute metrics (accuracy, F1, confusion matrix) in NumPy or
  torch instead of importing sklearn (M1).
- SARIMAX with a 52 season, DuckDB with three connections, `mlflow.sklearn.log_model`: known to fail under the cap (R4b).

## 5. Flaky results

Run the reference many times before shipping:

```bash
for i in 1 2 3 4 5; do pytest -q test_solution.py | tail -1; done
```

- Seed every random source and **pass the seed or generator into the solution**.
- Test on at least 3 seeds with a clear margin, never a borderline threshold.
- No `time.sleep` or real clock: inject a fake clock.
- Sets and dict order: sort before comparing, unless the statement defines order.
- Thread or async tests: use events and queues, never timing guesses.

## 6. After a fix

1. Re-run `validate` for the whole module (a changed shared `conftest.py` can break siblings).
2. If the cause was a library surprise, add one line to R4b in [docs/plans/README.md](../plans/README.md).
3. If the failure came from a wrong hand-traced value, write the correct derivation into `solution.md`.
4. Same problem failed validation **twice**: stop, and switch to Opus / high effort (CLAUDE.md).
