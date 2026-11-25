# Problem-writing playbook for the library tracks (swe, da, ds, ml, llm)

Read this **once per session** before writing problems for a module that uses libraries
(NumPy, pandas, statsmodels, scikit-learn, torch, Hugging Face, FastAPI, ...). It joins the
rules that are spread over three places into one path, and adds worked skeletons.

Sources it summarises (they win if they disagree, because they were measured):
[docs/plans/README.md](../plans/README.md) rules R1-R5, the track notes M1-M5 in
[ml.01-problem-plan.md](../plans/ml.01-problem-plan.md), and the *Testing notes* at the top of each plan.
Companion guides: [validation-triage.md](validation-triage.md) (a check fails),
[fixtures-and-data.md](fixtures-and-data.md) (data a problem needs).

## 0. Start of the session (5 minutes)

1. `./learn doctor <id>` lists packages the module's chapter imports and which are missing.
   It reads the chapter, not the plan, so also read the plan's "Testing notes".
2. Open the module's plan in `docs/plans/<id>-problem-plan.md`. Note: the ★ core set, the
   `assessment` problems, every `⚠ HAND-TRACE` row, and the *Risks* section at the bottom.
3. Open **one finished problem of the same track** as the format sample. Do not read more.
   Samples: da -> `content/da/da.03-pandas-core/problems/p001-*`; ds -> `content/ds/ds.01-*/problems/p001-*`;
   swe/llm/ml -> the first finished problem of that track once one exists (write it first and keep it small).
4. Check the Python rules that bite late: the local venv is **3.14**, CI is **3.11**.
   No `type X = ...`, no `def f[T]`, no backslash or same quote inside an f-string `{...}`.

## 1. The loop (one batch = 3-5 problems)

```bash
./learn new <id> "<title>" --tier <tier> --kind <kind>     # in plan order, makes every file from a template
# fill the files (section 2), then:
ulimit -v 1000000; ./learn validate <id> | tail -20
```

- Write **★ core problems first**. A module is usable once the core set validates.
- `validate` checks: files exist, >= 2 hints, `reference.py` passes, `starter.py` does **not** pass.
  It does **not** check that your tests are good, that the failure message is readable, that a trace
  answer is right, or that the problem runs on Windows or Python 3.11. Section 6 covers those.
- After the batch is green: add `✅` after each title in the plan, and update the README status row at the end.
- Use `./learn validate <id> -v` to list passes too. A failure: see [validation-triage.md](validation-triage.md).

## 2. Anatomy of a code problem

```text
pNNN-slug/
  problem.toml    id, title, tier, kind, topics, minutes, [assessment]
  problem.md      statement + one example + the interface of any helper the test gives
  hints.md        ## Hint 1 (a question) ... ## Hint 3 (pseudocode)
  solution.md     approach, code, cost, another way
  mistakes.md     the traps, each with the symptom the learner will see
  starter.py      the stub the learner gets (must FAIL, must be importable)
  reference.py    a correct solution (must PASS)
  test_solution.py   tests; every assert has a message that names the likely mistake
  conftest.py     (optional) fakes and fixtures shared by the tests
  fixtures/       (optional) small data files the TEST reads
```

Trace: `problem.md` holds the code, `expected.txt` the exact output. Explain: `answer.md` holds the model
answer and ends with a checklist of terms. `learn start` gives the learner **only** `starter.py`
(as `solution.py`) and `problem.md` (R1). Remember it when you write the statement.

### The four rules that decide whether a library problem is fair

1. **Data and helpers come in as arguments.** The solution never opens a fixture path and never
   imports a course helper. The test builds the data and passes it in (R1).
2. **No number that comes from randomness or training is hard-coded.** Compute the expected value
   from an obvious slow version, from the library, or check a property with a wide margin (R3).
3. **Time and memory:** whole test file about 20 s with the reference, peak memory under 1 GiB of
   *address space*. Tiny data, tiny models (R2, M1).
4. **A failing starter must fail readably.** Stubs define every name the test imports, return a wrong
   value of the right type, and the first assert's message tells the learner what to do.

### Skeleton: function style with a known-truth generator (ds, da)

`conftest.py` (generators are copied from the chapter so numbers match):

```python
import numpy as np
import pandas as pd
import pytest


def make_wages(n, seed):
    """Chapter 6.1 generator. True model: wage = 10 + 2.5 * years + noise."""
    rng = np.random.default_rng(seed)
    years = rng.uniform(0, 20, n)
    wage = 10 + 2.5 * years + rng.normal(0, 3, n)
    return pd.DataFrame({"years": years, "wage": wage})


@pytest.fixture
def wages():
    return make_wages(400, seed=0)
```

`test_solution.py`:

```python
import numpy as np
import pytest
import statsmodels.api as sm

from solution import fit_slope


def test_matches_statsmodels(wages):
    got = fit_slope(wages["years"].to_numpy(), wages["wage"].to_numpy())
    ref = sm.OLS(wages["wage"], sm.add_constant(wages["years"])).fit().params.to_numpy()
    np.testing.assert_allclose(got, ref, rtol=1e-8,
        err_msg="Compare with sm.OLS. Did you forget the intercept column, or divide by n instead of n-1?")


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_recovers_true_slope(seed):
    from conftest import make_wages
    d = make_wages(400, seed)
    slope = fit_slope(d["years"].to_numpy(), d["wage"].to_numpy())[1]
    assert abs(slope - 2.5) < 0.2, "On data with a known slope of 2.5 your slope is far off: check the formula, not the data."
```

A tolerance is chosen by running the reference on at least 3 seeds and picking a margin that all clear.

### Skeleton: torch (ml)

`conftest.py` (first lines, before NumPy is imported; M2):

```python
import os
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("MLFLOW_DISABLE_AGENT_HINT", "1")

import pytest
import torch


@pytest.fixture(autouse=True)
def one_thread():
    torch.set_num_threads(1)
```

Tests check **properties**, never a trained number (M5):

```python
def test_can_overfit_one_batch():
    torch.manual_seed(0)
    x, y = torch.randn(16, 4), torch.randint(0, 2, (16,))
    model = build_model()                      # from solution
    losses = train_steps(model, x, y, steps=150)
    assert losses[-1] < 0.2 * losses[0], "Loss did not fall on one batch. Check zero_grad(), the loss input (logits, not softmax) and the learning rate."


def test_shapes():
    out = build_model()(torch.randn(5, 4))
    assert out.shape == (5, 2), f"Expected logits of shape (5, 2), got {tuple(out.shape)}"
```

A torch test file imports **no** sklearn, scipy, pandas, mlflow or `datasets` (M1). Say so in `problem.md`.

### Skeleton: scripted fake LLM (llm)

```python
# conftest.py
import pytest


class ScriptedLLM:
    """Replies come from a list, in order. No network, no real model."""
    def __init__(self, replies):
        self.replies = list(replies)
        self.calls = []

    def __call__(self, system, messages):
        self.calls.append((system, messages))
        return self.replies.pop(0)


@pytest.fixture
def make_llm():
    return ScriptedLLM
```

The solution receives `llm` as an argument. A test that asserts what the prompt contained reads
`llm.calls`. Never print or invent what a real model would say; label scripted replies as scripted in `problem.md`.

## 3. Choosing the test strategy (decision list)

| The answer is... | Test it by |
|---|---|
| a formula on small inline data | hard-coded values you worked out on paper (hand-trace them) |
| a library result you rebuild by hand | `assert_allclose(mine, library(...), rtol=...)` |
| the output of random code or training | a property: shape, sums to 1, loss falls, accuracy over a wide threshold on 3 seeds |
| a fit to data from a known truth | "the CI contains the true value" or "error under a margin" on 3 seeds |
| a plot | inspect `Figure/Axes` objects (title, labels, counts, limits), never pixels (R4) |
| text a program prints | trace problem: print `.tolist()`, `int()`, `f"{x:.2f}"`, never a DataFrame or array repr (R3) |
| an external program (Postgres, Docker, Excel, a real LLM) | never run it. Test text (a YAML, a formula) or a Python model of it, or make it a trace/explain |

## 4. Mix and wording

- Tiers: drill (one idea), applied (realistic small task), deep (debug, trace, compare, internals), challenge (new mix of old topics).
- The `build` problem is the module project or a slice of it, usually the last one.
- Statements say what the function takes, returns and raises, and give one example with real values.
  Ambiguity is a bug in the statement, not in the learner: pin tie-breaks, rounding, empty input, order.
- `hints.md`: Hint 1 is a question, Hint 2 narrows, the last is pseudocode. Never the final code.
- `mistakes.md`: for each mistake, the symptom (the assert message the learner will see) and the fix.
- Only features and libraries taught in this module or earlier (check `requires:` in the syllabus entry).

## 5. Version traps seen so far (installed: Python 3.14, pandas 3, NumPy 2, scikit-learn 1.9)

Tutorials and free chatbots describe older versions. **Run every trace line and every reference before shipping.**
Known ones: NumPy 2 prints `np.float64(3.5)` for scalars; `CalibratedClassifierCV(cv="prefit")` is gone (use
`FrozenEstimator`); plotly 7 stores arrays in `to_dict()` in binary form; DuckDB 2.0 `1/0` is `inf`;
MLflow 3 returns params as strings. R4b in the plans README keeps the full list. **Add every new trap there**
the moment you meet it.

## 6. Before you tick a batch: the checks `validate` does not do

- [ ] Read the **starter's failure message** once (copy `starter.py` as `solution.py` next to the tests in a scratch
      folder and run pytest): it must say something useful, not `ImportError` or `NameError`.
- [ ] Every `assert` has a message that names a likely mistake.
- [ ] Reference passes on **3 seeds** where randomness exists; margin is clear, not borderline.
- [ ] Timing: `time pytest` on the reference is about 20 s or less, under `ulimit -v 1048576` with
      `OMP_NUM_THREADS=2 MALLOC_ARENA_MAX=2`.
- [ ] Every `⚠ HAND-TRACE` expected output was worked on paper **before** running the code, then compared.
- [ ] No test touches the network, a real clock (`time.sleep`) or the course repo's git.
- [ ] `encoding="utf-8"` on text opens, `pathlib` paths, `sys.executable` for child Python processes (R5).
- [ ] Python 3.11 syntax only (section 0, point 4). The CI job "Python 3.11" runs `pytest`, which lints chapters.
- [ ] Statement example matches what the reference returns.
- [ ] Nothing was written to `my-work/` or `data/progress.db`.

## 7. Models and effort (from CLAUDE.md, repeated so this guide stands alone)

Sonnet / medium for most modules. Opus / high for ml.01-ml.05, ds.04, ds.06 and any module with many
`⚠ HAND-TRACE` rows or tight memory (ml.05). Haiku / low for tutoring and chores. One module per session.
