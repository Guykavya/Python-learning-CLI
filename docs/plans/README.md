# Problem plans: index and shared rules

Every module that still needs problems has a plan here: `docs/plans/<id>-problem-plan.md`.
A plan lists every problem (number, title, tier, kind, the idea and what the tests check), so the
problems can be written later **one small batch at a time**, by Claude Code or by a free chatbot
([free-tier-authoring.md](../guides/free-tier-authoring.md)), without re-planning the module.

The format of every plan follows [dsa.07-problem-plan.md](dsa.07-problem-plan.md). The rules below
apply to all plans; the rules in a single plan win when they are more specific.

## How to write a module from its plan

1. Read this file (once), then the module's plan. Do not re-read the whole chapter: the plan names the
   chapter sections (`Ch. 5`) each problem rests on; read only those sections when a problem needs them.
2. Make the problem folders with `./learn new <id> "<title>" --tier <tier> --kind <kind>`, in plan order.
3. Fill the files in batches of 3–5 problems. Use one finished problem of the **same track** as the
   format sample (the first problem written in a track becomes the sample for the rest of that track).
4. `ulimit -v 1000000; ./learn validate <id> | tail -20` after every batch. Fix the test or the reference
   only after checking which one disagrees with `problem.md`.
5. Tick the plan: add `✅` after the title of every validated problem, so the next session knows where to start.
6. When a module is finished, change its row in the status table below.

## Status (2026-11-20)

Written = problem folders on disk. Plan = file in this folder.

| Module | Title | Problems | Written | Plan |
|---|---|---|---|---|
| core.01–core.24 | all core modules | 1,050 | 1,050 | not needed |
| shared.01–02 | SQL, pipelines | 105 | 105 | not needed |
| dsa.00–dsa.13 | | 610 | 610 | dsa.07–13 kept for reference |
| dsa.14 | Dynamic programming | 80 | 80 | done 2026-11-19, all validated |
| dsa.15 | Tries and string algorithms | 30 | 30 | done 2026-11-19, all validated |
| dsa.16 | Advanced data structures | 30 | 30 | done 2026-11-19, all validated |
| dsa.17 | Competitive programming in Python | 20 | 20 | done 2026-11-19, all validated |
| swe.01 | Working like an engineer | 20 | 20 | done 2026-11-19, all validated |
| swe.02 | Networking and HTTP | 35 | 35 | done 2026-11-19, all validated |
| swe.03 | Databases for backend engineers | 55 | 55 | done 2026-11-19, all validated |
| swe.04 | Flask | 40 | 40 | done 2026-11-19, all validated |
| swe.05 | FastAPI | 50 | 50 | done 2026-11-20, all validated |
| swe.06 | Django essentials | 25 | 25 | done 2026-11-20, all validated |
| swe.07 | Auth, API design and security | 35 | 35 | done 2026-11-20, all validated |
| swe.08 | Caching, queues and background work | 30 | 30 | done 2026-11-20, all validated |
| swe.09 | Deployment, observability and operations | 30 | 0 | yes |
| swe.10 | Practical architecture and system design | 25 | 0 | yes |
| swe.11 | Automation and scripting | 30 | 0 | yes |
| da.01 | Analysis environment and descriptive statistics | 30 | 0 | yes |
| da.02 | NumPy | 50 | 0 | yes |
| da.03 | pandas core | 60 | 0 | yes |
| da.04 | pandas transformations | 60 | 0 | yes |
| da.05 | Data cleaning and missing-data reasoning | 40 | 0 | yes |
| da.06 | Analytical thinking and metric correctness | 45 | 0 | yes |
| da.07 | SQL for analysts | 40 | 0 | yes |
| da.08 | Statistical reasoning for analysts | 35 | 0 | yes |
| da.09 | Data visualisation | 40 | 0 | yes |
| da.10 | EDA, reporting and communication | 30 | 0 | yes |
| da.11 | Applied business analytics | 30 | 0 | yes |
| da.12 | Excel for analysts | 30 | 0 | yes |
| da.13 | Power BI and data modelling (companion) | 20 | 0 | yes |
| ds.01 | Mathematics for data science | 60 | 0 | yes |
| ds.02 | Statistical modelling | 35 | 0 | yes |
| ds.03 | Machine learning fundamentals | 40 | 0 | yes |
| ds.04 | Evaluation done right | 45 | 0 | yes |
| ds.05 | scikit-learn in depth | 45 | 0 | yes |
| ds.06 | ML algorithms (from scratch and with libraries) | 60 | 0 | yes |
| ds.07 | Time-series forecasting | 35 | 0 | yes |
| ds.08 | Other special data | 30 | 0 | yes |
| ds.09 | Experimentation and causal inference | 30 | 0 | yes |
| ds.10 | Interpretation and communication | 20 | 0 | yes |
| ml.01 | Deep learning fundamentals | 40 | 0 | yes |
| ml.02 | PyTorch | 40 | 0 | yes |
| ml.03 | Computer vision | 25 | 0 | yes |
| ml.04 | Sequence models and transformers | 35 | 0 | yes |
| ml.05 | Fine-tuning pretrained models | 30 | 0 | yes |
| ml.06 | MLOps | 30 | 0 | yes |
| ml.07 | Model optimisation and deployment | 20 | 0 | yes |
| llm.01 | LLM fundamentals for builders | 20 | 0 | yes |
| llm.02 | Calling LLM APIs reliably | 30 | 0 | yes |
| llm.03 | Retrieval-augmented generation | 35 | 0 | yes |
| llm.04 | Evaluating LLM applications | 25 | 0 | yes |
| llm.05 | Tool use and agents | 30 | 0 | yes |
| llm.06 | Security for LLM applications | 25 | 0 | yes |
| llm.07 | Shipping LLM applications | 20 | 0 | yes |

Still to write: about 1,780 problems. **You do not have to write them all.** A module is usable as soon as
some problems validate. If time runs short, write the problems marked **★ core set** in each plan first
(about 40% of the module: the problems that cover every learning outcome once), then lower `problems:` in
`syllabus.yaml` to the number actually written. 20 good problems beat 50 shaky ones.

Suggested order (follows the levels, essentials first): dsa.14 rest → swe.01–05, swe.07 → llm.01–06 →
da.01–08 → ds.01–05 → ml.01–02 → everything else. Every plan has a ★ core set; write those first.

Model per module: Sonnet/medium for most; Opus/high for ml.01–ml.05, ds.04, ds.06, dsa.14's rest and any module whose plan
has many ⚠ HAND-TRACE rows or tight memory (ml.05). Haiku/low for tutoring and chores.

Open decision for Kavya (engine change, not made): a per-problem memory setting in `problem.toml` (ml.05 sits ~50 MB under the cap).

## Rules for every plan (all tracks)

From CLAUDE.md, repeated here so a plan can be used alone:

- Count = `problems:` in the syllabus. Mix about 1/3 drill, 1/3 applied, rest deep + challenge.
  Mostly `code`; about 10 `trace` and 5 `explain` in a big module, fewer in a small one (20 problems: ~5 trace, ~3 explain).
- Exactly one problem each with `assessment = "explain" | "trace" | "fix" | "build"`. The `build` one is
  the module project (or a small slice of it), usually the last problem.
- Every problem: `problem.toml`, `problem.md` (with an example), `hints.md` (≥ 2 hints, question → pseudocode),
  `solution.md` (approach, code, complexity or cost, another way), `mistakes.md`.
  Code problems: `starter.py` (must FAIL), `reference.py` (must PASS), `test_solution.py`.
  Trace: `expected.txt`. Explain: `answer.md`.
- Function style: `from solution import f`. Every assert has a message naming the likely mistake.
- Only features taught in this module or earlier (check the module's `requires:` in the syllabus).
- Code must parse on **Python 3.11**: no `type X = ...`, no PEP 695 generics (`def f[T]`), no backslash or
  the f-string's own quote inside `{...}`. The local venv is 3.14, so 3.11-only breakage will not show locally.
- **⚠ HAND-TRACE** in a plan marks a test with step-by-step expected output. Work it out on paper, then run
  the code and compare (core.04.p058 shipped wrong because nobody did).
- **Explain** problems are self-rated by the learner against `answer.md`. "Graded by terms" in a plan means
  `answer.md` ends with a checklist of those terms/points; nothing is auto-graded.
- Infinite or huge inputs: a `starter.py` stub never loops over or `list()`s what a test makes infinite or huge.

## Rules for the library tracks (swe, da, ds, ml, llm)

These come from how the engine actually runs tests (`engine/learn/runner.py`, `cli.py`) and from measuring
the libraries under the runner's limits on 2026-11-18. Breaking one of them gives a problem that passes
`learn validate` but fails for the learner, or the other way round.

### R1. What the runner copies, and what the learner gets

- `learn check` copies into a temporary folder: the learner's files with suffix `.py .txt .csv .json .md .toml .yaml .yml`,
  then `test_solution.py`, `conftest.py` (if the problem has one) and the whole `fixtures/` folder.
  `.xlsx .ipynb .sql .parquet .png .pdf` files **in the learner's folder are not copied**.
- `learn start` puts **only `starter.py` (as `solution.py`) and `problem.md`** in `my-work/`. No fixtures, no conftest.
- So: **the learner's code never opens a fixture path and never imports a course helper.** Data and helpers reach
  the solution as **function arguments**. The test builds them (inline, from a generator in the test file, or
  from `Path(__file__).parent / "fixtures" / ...`) and passes them in. Files the solution must write go to a
  path the test passes in (`tmp_path`).
- Shared fakes (FakeLLM, FakeRedis, a fake clock, the chapter's mini Excel evaluator, dataset generators) live in
  the problem's `conftest.py` or at the top of `test_solution.py`. `problem.md` shows their interface (and, when
  short, the full code in a collapsible block) so the learner can experiment in `my-work/` by copying it.
- SQL answers: `QUERY = """..."""` in `solution.py` (the shared.01 convention), data inline in the test.
- Possible small engine change, **not done** (ask Kavya first): `learn start` also copies `fixtures/` into
  `my-work/<problem>/`. Plans do not depend on it.

### R2. Limits: 60 seconds, 1 GiB address space, no network

- The whole `test_solution.py` must finish in **about 20 s** with the reference (the cap is 60 s; Windows and
  older laptops are slower, and `validate` runs the starter too). Measured import costs under the cap:
  numpy 0.2 s · pandas 1.1 s · sklearn 2.7 s · statsmodels 3.0 s · torch 3.3 s · tiny BERT + LoRA forward/backward 8 s.
- Peak memory well under 1 GiB: measured torch MLP + conv 350 MB, tiny BERT + peft 455 MB. Keep models tiny
  (hidden size ≤ 64, ≤ 2 layers) and data small (≤ 5,000 rows, images ≤ 32×32).
- No network ever. No `from_pretrained("name")`, no `load_dataset("name")`, no `pip install`, no real HTTP
  outside `127.0.0.1`. Tests set `HF_HUB_OFFLINE=1` (via `monkeypatch.setenv` or at the top of the file).
  Hugging Face models are built from a small config (`BertConfig(vocab_size=200, hidden_size=32, num_hidden_layers=2,
  num_attention_heads=2, intermediate_size=64)`), tokenisers from a local vocabulary.
- **Not installed** in the course environment (do not plan problems that need them): `torchvision`, `shap`,
  `xgboost`, `lightgbm`, `umap-learn`, `playwright`, `redis`, `fakeredis`. Installed and usable: numpy, pandas,
  polars, pandera, pyarrow, duckdb, scipy, statsmodels, matplotlib, seaborn, plotly, streamlit, openpyxl,
  scikit-learn, torch (CPU), transformers, tokenizers, datasets (local data only), peft, onnx, onnxruntime,
  onnxscript, mlflow, dvc, celery, flask, flask-sqlalchemy, fastapi, sqlmodel, sqlalchemy, alembic, aiosqlite,
  django, djangorestframework, pyjwt, requests, httpx, beautifulsoup4, nbformat, pypdf, hypothesis.
- Anything that needs an outside program (Postgres, Redis, Docker, Nginx, Power BI, Excel, a browser, cron,
  GitHub Actions, a real LLM provider) is **never run by a test**. Problems about them work on the text
  (a Dockerfile, a compose YAML, a DAX formula, an Nginx block, a crontab line), on a Python model of the
  behaviour, or are trace/explain problems. Never state what the real tool prints unless the chapter captured it.

### R3. Answers that do not change between machines and versions

- Seed everything: `random.Random(seed)`, `np.random.default_rng(seed)`, `torch.manual_seed(seed)`. Pass the
  seed or the generator into the solution when its randomness matters.
- **Do not hard-code numbers that come out of a library's randomness or training** (NumPy does not promise the
  same `Generator` stream across versions; torch results differ across CPUs). Instead compute the expected value
  in the test from a slow obvious version, or compare with the library (`sklearn`, `scipy`), or check a property
  (loss went down, accuracy ≥ a threshold with a wide margin on easy synthetic data, shapes, sums to 1).
  Hard-coded numbers only for small inline data the test author worked out.
- Floats: `pytest.approx` / `np.testing.assert_allclose` with a stated tolerance. ML quality thresholds: the
  reference must clear the threshold on at least 3 different seeds by a clear margin (check this when writing).
- **Trace problems with libraries:** never print a DataFrame, Series or array repr (it depends on terminal width,
  and NumPy 2 prints scalars as `np.float64(3.5)`). The traced code prints `.tolist()`, `.to_dict()`, `int(...)`,
  `float(...)`, or `f"{x:.2f}"`. Pin the library behaviour you rely on to one the chapter already ran.
- `torch.set_num_threads(1)` at the top of torch tests: faster under the cap and more repeatable.

### R4. Library-specific test patterns

| Library | Pattern |
|---|---|
| matplotlib / seaborn | first lines of the test: `import matplotlib; matplotlib.use("Agg")`. Inspect the returned `Figure`/`Axes` (titles, labels, number of lines/bars, `get_ylim()`, tick labels, colours), never pixels. `plt.close("all")` in a fixture. |
| plotly | read `fig.data[i].x` / `.y` / `.type` and `fig.layout.title.text`, axis ranges. **Not `fig.to_dict()`**: plotly 7 stores arrays there in binary form, not as lists (measured 2026-11-18). |
| pytest run by hand | set `OMP_NUM_THREADS=2 MALLOC_ARENA_MAX=2` before `ulimit -v 1048576`, as the runner does; scipy + plotly together raise `MemoryError` under the cap without it. |
| MiniXL / MiniDAX (da.12, da.13) | copy the exact line ranges the plan names into `conftest.py`, including the imports from the chapter's first code block; the chapter's §4.1 block alone raises `NameError`. |
| streamlit | `AppTest.from_file("solution.py", default_timeout=30)`; the app *is* `solution.py`; data comes from a function the test can monkeypatch, not a file. |
| openpyxl | openpyxl **does not calculate formulas**; a workbook it saved has no cached values. Tests read the formula text (`cell.value == "=SUMIFS(...)"`, normalised) and/or evaluate it with the chapter's mini evaluator placed in `conftest.py`, and compare with the pandas truth. |
| Flask / FastAPI | `app.test_client()` / `TestClient(app)`; an app factory `create_app(config)` so each test gets a fresh app and an in-memory SQLite database. |
| Django | settings via `settings.configure(...)` + `django.setup()` in `conftest.py`, in-memory SQLite. Models need an app: verify the approach on the first Django problem (see the swe.06 plan) before writing the rest. |
| SQLAlchemy / Alembic | `sqlite://` in memory or a file in `tmp_path`; Alembic run programmatically (`command.upgrade(cfg, "head")`) with a `script_location` the test creates. |
| git | real git only inside `tmp_path`, with `-c user.name=t -c user.email=t@example.com -c init.defaultBranch=main -c commit.gpgsign=false`, never in the course repository. Prefer functions that parse git output given as text. |
| subprocess | `sys.executable` for Python children, never `python`/`python3` by name (Windows). |
| torch | tiny models, ≤ 200 steps; check shapes, gradients (`torch.autograd.gradcheck` on float64), loss decrease, determinism with a seed; never an exact trained loss. |
| sklearn | compare with the library's own result (`np.testing.assert_allclose(mine, sk.coef_, rtol=1e-4)`) or with an obvious slow version. Ban leaking the test set by giving the solution only what it may see. |
| FakeLLM | the chapter's `FakeLLM` (llm.01 §1) in `conftest.py`, injected as an argument; scripted replies, usage, `stop_reason`, injectable errors, a fake clock instead of `time.sleep`. |

### R4b. Measured under the cap (2026-11-18); details are in each plan's Testing notes

- **Installed versions are new:** Python 3.14 locally, pandas 3.1, NumPy 2.5, Polars 2.1, DuckDB 2.0, plotly 7, scikit-learn 1.9,
  MLflow 3. Tutorials and free chatbots describe older behaviour. Run every trace line and every reference before shipping.
- **Memory is virtual address space.** torch + an optimiser ≈ 720 MB; adding sklearn, scipy, mlflow, `datasets` or pandas fails.
  A torch test imports no other heavy library (ml.01 plan, rules M1–M5). ml.05 peaks near 994 MB: a library update can break it.
  Set `OMP_NUM_THREADS=2 MALLOC_ARENA_MAX=2` (and `OPENBLAS_NUM_THREADS=1` in conftest when sklearn and torch meet).
- **DuckDB 2.0:** at most one or two connections open at once (three segfault under the cap); take the connection from a fixture
  that closes it; use `.df()` or `.fetchall()`, never `fetchone()` on a reused connection; `1/0` is `inf`, not NULL.
- **Django:** conftest pattern is spiked and works (see the swe.06 plan). A starter must define every name the test imports,
  or pytest stops at collection with 0 tests and `validate` still accepts it.
- **Flask templates:** `.html` files in `my-work/` are not copied; use a `TEMPLATES` dict with a Jinja `DictLoader`.
- **MLflow 3:** SQLite store in `tmp_path`; `mlflow.sklearn.log_model` fails under the cap; params come back as strings.
- **scikit-learn 1.9:** no `CalibratedClassifierCV(cv="prefit")`; use `FrozenEstimator`.
- **statsmodels:** SARIMAX with a 52-period season raises MemoryError; keep seasons ≤ 12 and backtests ≤ 5 refits.
- **Not installed (more):** `pydantic-settings`, `typer` (importable by accident only), `tiktoken`. Use argparse/Click, hand-written settings.
- **Symlinks, process checks and real `git`** need care on Windows: skip that one test, never the whole problem.
- A problem whose `starter.py` is an empty stub passes `validate` but must still give a readable failure: stubs define every imported name.

### R5. Windows and portability

`encoding="utf-8"` on every text open, `newline=""` for CSV, `pathlib` paths, no `fork`-only multiprocessing,
no shell features in `subprocess` calls, no file names with `:`.

## Format of each plan

```
# Problem plan: <id> <title> (<N> problems)
Rules: docs/plans/README.md (shared) and dsa.07-problem-plan.md (table format). Ids <id>.p001…, folder pNNN-slug.
**Mix:** … **Kinds:** … **assessment:** explain = pX, trace = pY, fix = pZ, build = pW.
**★ core set:** the ~40% to write first.
**Testing notes:** helpers in conftest.py, data, time/memory, anything spiked and its measured result.

## A. <group> (Ch. a–b)
| # | Title | Tier | Kind | Idea / what the tests check |
...
## Counts check
## Risks and open questions
```
