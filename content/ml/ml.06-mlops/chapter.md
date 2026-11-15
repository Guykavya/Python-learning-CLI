# Chapter 6 (ML): MLOps

In ml.02 to ml.05 you trained models. In real work, training is the easy part. The hard questions come after: *Which run produced the model that is live right now? Can you rebuild it? Which data did it see? Why do predictions in production differ from the notebook? Is it still any good three months later?* **MLOps** is the set of habits and tools that answer those questions: **tracking** every experiment, **versioning** data and models, **serving** a model as a reliable service, keeping **training and serving consistent**, **monitoring** for drift, and running **tests and gates** (CI) before anything goes live.

You will build every idea once by hand (so you know what the tools actually do) and then use the real tool: **MLflow** for experiment tracking and the model registry, **DVC** for data and pipeline versioning, **FastAPI + Docker** for serving. The two syllabus outcomes are **reproduce any past experiment from its tracked config** and **detect drift in a served model**; the project deploys a model as a service and monitors it.

Prerequisites: ml.02 (PyTorch/training loops; here the models are scikit-learn so everything runs in seconds), swe.09 (Docker, CI, logs and metrics), ds.04 (honest evaluation), ml.05 (paired tests).

> **How this chapter is built.** The examples that carry the main lessons are real runs, with the output pasted exactly as the computer printed it (MLflow 3.18, DVC 3.67, FastAPI, Docker 29, all on this machine). Variations that would only repeat a lesson are **question → worked answer** boxes, with no invented numbers. Sections carry optional **Visualise it** prompts you can paste into any AI chat; the course never depends on them. Everything uses a **synthetic customer dataset that we generate ourselves**, so the effects (drift, skew, leakage) have *known causes* and you can check the tools against the truth.
>
> **What needs the internet.** MLflow and DVC run fully locally. Only the Docker tutorial (section 5.3) needs the internet **once**: to pull the `python:3.14-slim` base image (about 45 MB compressed) and to download the library wheels it installs. Docker commands here only touch resources named `pbtut-*` and bind to `127.0.0.1`; nothing else on the machine is started, stopped or removed. If Docker is not available on your machine, skip 5.3; the rest works without it.

```python run
import os, sys, json, math, time, hashlib, platform, pathlib, tempfile, subprocess, shutil, warnings, contextlib, datetime as dt
os.environ["MLFLOW_DISABLE_AGENT_HINT"] = "1"
import numpy as np
import pandas as pd
import scipy, sklearn, joblib, mlflow
warnings.filterwarnings("ignore")
np.set_printoptions(precision=4, suppress=True, linewidth=120)
pd.set_option("display.width", 140); pd.set_option("display.max_columns", 30)

ws = pathlib.Path(tempfile.mkdtemp(prefix="mlops_ws_"))            # every file this chapter creates lives here
print("python  ", sys.version.split()[0], "|", platform.system())
print("numpy   ", np.__version__, "| pandas", pd.__version__, "| scikit-learn", sklearn.__version__, "| scipy", scipy.__version__)
print("mlflow  ", mlflow.__version__)
print("workspace:", ws.name)
```
```text
python   3.14.4 | Linux
numpy    2.5.4 | pandas 3.1.1 | scikit-learn 1.9.1 | scipy 1.18.1
mlflow   3.18.0
workspace: mlops_ws_5u9o_3ij
```

## Table of contents

1. [Why MLOps: the reproducibility problem](#1-why-mlops-the-reproducibility-problem)
2. [Experiment tracking: by hand, then MLflow](#2-experiment-tracking-by-hand-then-mlflow)
3. [Versioning data and pipelines with DVC](#3-versioning-data-and-pipelines-with-dvc)
4. [The model registry and promotion gates](#4-the-model-registry-and-promotion-gates)
5. [Serving a model: FastAPI, then Docker](#5-serving-a-model-fastapi-then-docker)
6. [Training-serving consistency](#6-training-serving-consistency)
7. [Monitoring and drift](#7-monitoring-and-drift)
8. [CI for ML and safe releases](#8-ci-for-ml-and-safe-releases)
9. [Project: deploy and monitor a model as a service](#9-project-deploy-and-monitor-a-model-as-a-service)
10. [Common traps](#10-common-traps)
11. [Summary](#11-summary)

## 1. Why MLOps: the reproducibility problem

### 1.1 A model is not just code

Software is mostly its code. A trained model is the product of **five** things, and losing any one makes it impossible to rebuild:

| Ingredient | Example | If you lose it |
|---|---|---|
| **Code** | `train.py`, the feature function | you cannot tell what logic produced the numbers |
| **Data** | the exact rows, after exactly this cleaning | the same code gives different models |
| **Configuration** | learning rate, `max_depth`, train/test split, **random seed** | you guess the settings |
| **Environment** | Python, scikit-learn, NumPy versions | results (and even pickles) change or break |
| **Randomness** | weight init, data order, dropout | two runs disagree |

MLOps starts by treating all five as things to *record* at every run. Here is why, in one cell. We create the customer data used throughout the chapter: a subscription company, one row per customer, the target is whether the customer **churned** (left) in the next month.

```python run
PLANS, REGIONS = ["basic", "standard", "premium"], ["north", "south", "east", "west"]
NUM, CAT, TARGET = ["tenure_months", "monthly_spend", "support_tickets"], ["plan", "region"], "churned"

def make_customers(n, seed=0, spend_shift=1.0, premium_boost=0.0, concept=0.0):
    """Synthetic customers with a KNOWN churn rule.
    spend_shift   multiplies spend (a data-drift knob), premium_boost moves 'premium' share up (another drift knob),
    concept       > 0 changes HOW support tickets relate to churn (a concept-drift knob)."""
    rng = np.random.default_rng(seed)
    plan = rng.choice(PLANS, n, p=[0.50 - premium_boost, 0.35, 0.15 + premium_boost])
    base = pd.Series(plan).map({"basic": 25.0, "standard": 45.0, "premium": 80.0}).to_numpy()
    spend = (base * rng.lognormal(0.0, 0.30, n) * spend_shift).round(2)
    tenure = rng.gamma(2.0, 12.0, n).round(1)
    tickets = rng.poisson(1.2, n)
    region = rng.choice(REGIONS, n)
    z = -0.7 - 0.035 * tenure + (0.45 - 0.9 * concept) * tickets + 0.008 * (spend - base * spend_shift) + (plan == "premium") * -0.5
    churned = (rng.random(n) < 1 / (1 + np.exp(-z))).astype(int)
    return pd.DataFrame({"customer_id": np.arange(n), "tenure_months": tenure, "monthly_spend": spend, "support_tickets": tickets,
                         "plan": plan, "region": region, TARGET: churned})

df = make_customers(6000, seed=0)
print(df.head(4).to_string(index=False))
print(f"\n{len(df)} customers, churn rate {df[TARGET].mean():.3f}")
```
```text
 customer_id  tenure_months  monthly_spend  support_tickets     plan region  churned
           0           19.4          36.95                3 standard   west        1
           1           15.7          35.31                3    basic  south        0
           2           14.2          19.24                1    basic   west        1
           3            6.9          21.98                0    basic   east        1

6000 customers, churn rate 0.289
```

### 1.2 The same code, two answers

Train a random forest twice, same data, same code, and compare. This is the experience that makes people feel "my result is gone":

```python run
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder

train_df, test_df = train_test_split(df, test_size=0.25, random_state=0, stratify=df[TARGET])      # fixed split
def preprocess(): return ColumnTransformer([("num", StandardScaler(), NUM), ("cat", OneHotEncoder(handle_unknown="ignore"), CAT)])

for attempt in (1, 2):
    pipe = Pipeline([("prep", preprocess()), ("model", RandomForestClassifier(n_estimators=60, min_samples_leaf=5, n_jobs=1))])      # no random_state!
    pipe.fit(train_df[NUM + CAT], train_df[TARGET])
    print(f"unseeded run {attempt}: test AUC {roc_auc_score(test_df[TARGET], pipe.predict_proba(test_df[NUM + CAT])[:, 1]):.5f}")
for attempt in (1, 2):
    pipe = Pipeline([("prep", preprocess()), ("model", RandomForestClassifier(n_estimators=60, min_samples_leaf=5, n_jobs=1, random_state=7))])
    pipe.fit(train_df[NUM + CAT], train_df[TARGET])
    print(f"seeded   run {attempt}: test AUC {roc_auc_score(test_df[TARGET], pipe.predict_proba(test_df[NUM + CAT])[:, 1]):.5f}")
```
```text
unseeded run 1: test AUC 0.64576
unseeded run 2: test AUC 0.65678
seeded   run 1: test AUC 0.65044
seeded   run 2: test AUC 0.65044
```

The unseeded runs disagree in the third or fourth decimal; the seeded ones agree to the last digit. The difference is small here, but the day someone asks "can you reproduce the 0.8412 from March?" only the seeded, recorded run can. A seed is a **parameter** and belongs in the tracked configuration like any other.

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw the five ingredients of a trained model (code, data, configuration including the random seed, environment with library versions, randomness) as five labelled boxes with arrows into a box called 'trained model'. Then show a second picture where each box is stamped with a fingerprint (git commit, data hash, config file, lockfile, seed) and an arrow into a 'run record'. Label the first picture 'cannot rebuild' and the second 'can rebuild'."

### 1.3 The lifecycle

```
 data ──> train ──> evaluate ──> register ──> deploy/serve ──> monitor ──┐
  ▲                                                                       │
  └──────────────── retrain when the world changes (drift) <──────────────┘
        every arrow is something to automate, test and record
```

This chapter follows the loop: section 2 (train and record), 3 (data), 4 (register and gate), 5 and 6 (serve), 7 (monitor), 8 (automate), and the project closes the loop.

### 1.4 Try it

1. List the five ingredients for the last model you trained in ml.05. Which could you reproduce today, and which not?
2. Why does `n_jobs=-1` (parallel trees) make bit-exact reproducibility harder even with a seed? (Think about the order in which results are combined.)

## 2. Experiment tracking: by hand, then MLflow

### 2.1 What a run record should contain

An **experiment tracker** stores, for every training run, a record: the **parameters**, the **metrics**, the **artifacts** (model file, plots), and the **context** (data fingerprint, code version, environment, time). Before using a tool, write the smallest tracker that works. About 40 lines:

```python run
import uuid, contextlib, getpass

def file_sha256(path, n=16):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""): h.update(chunk)
    return h.hexdigest()[:n]

class RunHandle:
    def __init__(self, record, folder): self.record, self.folder = record, folder
    def log_metric(self, key, value): self.record["metrics"][key] = float(value)
    def log_artifact(self, path):
        shutil.copy(path, self.folder / pathlib.Path(path).name); self.record["artifacts"].append(pathlib.Path(path).name)

@contextlib.contextmanager
def tracked_run(root, name, params, data_file):
    root = pathlib.Path(root); root.mkdir(parents=True, exist_ok=True)
    run_id = f"run{len(list(root.iterdir())) + 1:03d}"
    folder = root / run_id; folder.mkdir()
    record = {"run_id": run_id, "name": name, "started": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
              "params": params, "metrics": {}, "artifacts": [],
              "data": {"file": str(data_file), "sha256": file_sha256(data_file)},
              "env": {"python": platform.python_version(), "scikit-learn": sklearn.__version__, "numpy": np.__version__}}
    t0 = time.time()
    run = RunHandle(record, folder)
    try:
        yield run
        record["status"] = "FINISHED"
    except Exception as e:
        record["status"] = f"FAILED: {e}"; raise
    finally:
        record["seconds"] = round(time.time() - t0, 2)
        (folder / "run.json").write_text(json.dumps(record, indent=2), encoding="utf-8")

print("tracker defined: a run = a folder with run.json (params, metrics, data hash, environment) + artifacts")
```
```text
tracker defined: a run = a folder with run.json (params, metrics, data hash, environment) + artifacts
```

Now an experiment function whose *only* inputs are `params` and the data file, which is exactly what makes it reproducible, and four runs through the tracker:

```python run
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import GradientBoostingClassifier

data_file = ws / "customers.csv"; df.to_csv(data_file, index=False)

def run_experiment(params, data_path):
    d = pd.read_csv(data_path)
    tr, te = train_test_split(d, test_size=params["test_size"], random_state=params["seed"], stratify=d[TARGET])
    if params["model"] == "logreg":
        model = LogisticRegression(C=params["C"], max_iter=1000)
    else:
        model = GradientBoostingClassifier(n_estimators=params["n_estimators"], max_depth=params["max_depth"], learning_rate=0.1, random_state=params["seed"])
    pipe = Pipeline([("prep", preprocess()), ("model", model)]).fit(tr[NUM + CAT], tr[TARGET])
    p = pipe.predict_proba(te[NUM + CAT])[:, 1]
    return pipe, {"auc": roc_auc_score(te[TARGET], p), "accuracy": float(((p > 0.5) == te[TARGET]).mean())}

configs = [dict(model="logreg", C=1.0, seed=0, test_size=0.25), dict(model="logreg", C=0.05, seed=0, test_size=0.25),
           dict(model="gbm", n_estimators=100, max_depth=2, seed=0, test_size=0.25), dict(model="gbm", n_estimators=200, max_depth=3, seed=0, test_size=0.25)]
runs_root = ws / "myruns"
for i, cfg_ in enumerate(configs):
    with tracked_run(runs_root, f"exp{i}", cfg_, data_file) as run:
        pipe_, m = run_experiment(cfg_, data_file)
        for k, v in m.items(): run.log_metric(k, v)
        joblib.dump(pipe_, ws / "model.joblib"); run.log_artifact(ws / "model.joblib")

records = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(runs_root.glob("run*/run.json"))]
tbl = pd.DataFrame([{"run": r["run_id"], "model": r["params"]["model"], "C": r["params"].get("C"), "depth": r["params"].get("max_depth"),
                     "trees": r["params"].get("n_estimators"), "auc": round(r["metrics"]["auc"], 5), "acc": round(r["metrics"]["accuracy"], 4), "sec": r["seconds"]} for r in records])
print(tbl.to_string(index=False))
print("\nwhat one record holds:", {k: (v if k != 'params' else '...') for k, v in list(records[2].items())[:3]}, "... data sha256", records[2]["data"]["sha256"])
```
```text
   run  model    C  depth  trees     auc    acc  sec
run001 logreg 1.00    NaN    NaN 0.69055 0.7300 0.02
run002 logreg 0.05    NaN    NaN 0.69177 0.7307 0.03
run003    gbm  NaN    2.0  100.0 0.68577 0.7220 0.26
run004    gbm  NaN    3.0  200.0 0.67286 0.7073 0.63

what one record holds: {'run_id': 'run003', 'name': 'exp2', 'started': '2026-11-13T13:56:32+00:00'} ... data sha256 fdd7ed8b31aec4de
```

### 2.2 The outcome: reproduce a past run from its record

The test of a tracker is whether `reproduce(run_id)` brings back the same numbers. Our version reads the stored config, **refuses to run if the data changed**, retrains, and compares:

```python run
def reproduce(root, run_id, data_path):
    rec = json.loads((pathlib.Path(root) / run_id / "run.json").read_text(encoding="utf-8"))
    if file_sha256(data_path) != rec["data"]["sha256"]:
        raise RuntimeError(f"data changed since {run_id}: recorded {rec['data']['sha256']}, now {file_sha256(data_path)}")
    if rec["env"]["scikit-learn"] != sklearn.__version__:
        print("warning: scikit-learn version differs from the recorded one; small numeric differences are possible")
    _, m = run_experiment(rec["params"], data_path)
    return {k: (rec["metrics"][k], m[k], rec["metrics"][k] == m[k]) for k in rec["metrics"]}

print("reproduce run003:", reproduce(runs_root, "run003", data_file))
changed = ws / "customers_changed.csv"
df.assign(monthly_spend=df.monthly_spend * 1.01).to_csv(changed, index=False)           # a 1% change in one column
try: reproduce(runs_root, "run003", changed)
except RuntimeError as e: print("reproduce on changed data ->", e)
```
```text
reproduce run003: {'auc': (0.6857681067948573, 0.6857681067948573, True), 'accuracy': (0.722, 0.722, True)}
reproduce on changed data -> data changed since run003: recorded fdd7ed8b31aec4de, now 146bd9db85987ee0
```

Bit-identical metrics from the record alone, and a loud refusal when the data silently changed. Everything MLflow adds is convenience around this idea: a database instead of folders, a UI to compare runs, standard places for models and plots, and integrations.

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw a 'run record' as a card with four sections: params (model=gbm, n_estimators=200, max_depth=3, seed=0), metrics (auc, accuracy), data fingerprint (sha256 of customers.csv), environment (python, scikit-learn, numpy). Then draw the reproduce step as a flow: read the card, compare the data hash with the file on disk (green tick or red stop 'data changed'), retrain, compare metrics, print 'identical'."

### 2.3 MLflow

**MLflow Tracking** is a library plus a store. You wrap a run in `mlflow.start_run()` and call `log_params`, `log_metrics`, `log_artifact`, `log_model`. The store has two parts: a **backend store** (parameters and metrics: a SQLite file here, a database server in production) and an **artifact store** (files: a folder here, S3 or a shared disk in production). We point both at our workspace so nothing leaks into the repository.

```python run
mlflow.set_tracking_uri(f"sqlite:///{ws / 'mlflow.db'}")
art_root = (ws / "mlartifacts").as_uri()
if mlflow.get_experiment_by_name("churn") is None:
    mlflow.create_experiment("churn", artifact_location=art_root)
mlflow.set_experiment("churn")
from mlflow.models import infer_signature

run_ids = {}
t0 = time.time()
for i, cfg_ in enumerate(configs):
    with mlflow.start_run(run_name=f"{cfg_['model']}-{i}") as r:
        mlflow.log_params(cfg_)
        mlflow.set_tags({"data_sha256": file_sha256(data_file), "dataset": "customers.csv", "stage": "experiment"})
        pipe_, m = run_experiment(cfg_, data_file)
        mlflow.log_metrics(m)
        X_example = df[NUM + CAT].head(5)
        mlflow.sklearn.log_model(pipe_, name="model", serialization_format="cloudpickle", signature=infer_signature(X_example, pipe_.predict(X_example)), input_example=X_example)
        run_ids[i] = r.info.run_id
print(f"4 runs logged in {time.time() - t0:.1f}s | tracking store: {pathlib.Path(mlflow.get_tracking_uri().split('///')[1]).name}")
runs = mlflow.search_runs(experiment_names=["churn"], order_by=["metrics.auc DESC"])
cols = ["tags.mlflow.runName", "params.model", "params.C", "params.max_depth", "params.n_estimators", "metrics.auc", "metrics.accuracy"]
print(runs[cols].round(4).to_string(index=False))
```
```text
4 runs logged in 10.4s | tracking store: mlflow.db
tags.mlflow.runName params.model params.C params.max_depth params.n_estimators  metrics.auc  metrics.accuracy
           logreg-1       logreg     0.05              NaN                 NaN       0.6918            0.7307
           logreg-0       logreg      1.0              NaN                 NaN       0.6906            0.7300
              gbm-2          gbm      NaN                2                 100       0.6858            0.7220
              gbm-3          gbm      NaN                3                 200       0.6729            0.7073
```

A note on `serialization_format="cloudpickle"`: a pickle file can run arbitrary code when it is loaded, so you only ever load model files from sources you trust. Recent MLflow versions default to the safer **skops** format, which refuses to load types it has not been told to trust; for a tutorial with our own files we choose cloudpickle, and in a team you would keep skops (and list the reviewed types in `skops_trusted_types`) or load only from a registry you control.

`search_runs` returns a DataFrame, so "show me every run on this dataset with AUC above X" is one line of pandas. In a real project you also start the UI with `mlflow ui --backend-store-uri sqlite:///mlflow.db` and compare runs side by side in a browser (shown, not run, here).

**Model signature and loading.** `infer_signature` records the model's input columns and types. It is a small contract that a serving layer can check. A logged model is loaded back by run id and used like any scikit-learn pipeline, even from a different process:

```python run
best_id = runs.iloc[0]["run_id"]
print("best run:", runs.iloc[0]["tags.mlflow.runName"], "| id", best_id[:8], "...")
info = mlflow.models.get_model_info(f"runs:/{best_id}/model")
print("signature inputs :", [f"{c.name}:{c.type}" for c in info.signature.inputs.inputs][:6], "...")
print("signature outputs:", info.signature.outputs)
loaded = mlflow.sklearn.load_model(f"runs:/{best_id}/model")
print("loaded model predicts the same as the one we trained:",
      bool(np.allclose(loaded.predict_proba(test_df[NUM + CAT])[:, 1], run_experiment(configs[int(runs.iloc[0]['tags.mlflow.runName'].split('-')[1])], data_file)[0].predict_proba(test_df[NUM + CAT])[:, 1])))
```
```text
best run: logreg-1 | id 259f1ebf ...
signature inputs : ['tenure_months:DataType.double', 'monthly_spend:DataType.double', 'support_tickets:DataType.long', 'plan:DataType.string', 'region:DataType.string'] ...
signature outputs: [Tensor('int64', (-1,))]
loaded model predicts the same as the one we trained: True
```

### 2.4 Reproduce from MLflow

Everything needed is in the run: parameters, the `data_sha256` tag, the environment (MLflow also stores a `requirements.txt` and `conda.yaml` next to the model). The same function, now reading MLflow:

```python run
def reproduce_mlflow(run_id, data_path):
    run = mlflow.get_run(run_id)
    params = {k: (float(v) if k in ("C", "test_size") else int(v) if k in ("n_estimators", "max_depth", "seed") else v) for k, v in run.data.params.items()}
    if run.data.tags["data_sha256"] != file_sha256(data_path):
        raise RuntimeError("data changed since this run")
    _, m = run_experiment(params, data_path)
    return {k: (run.data.metrics[k], m[k], abs(run.data.metrics[k] - m[k]) < 1e-12) for k in run.data.metrics}

print("reproduce the best run from MLflow:", reproduce_mlflow(best_id, data_file))
art_dir = pathlib.Path(mlflow.artifacts.download_artifacts(f"runs:/{best_id}/model", dst_path=str(ws / "downloaded")))
print("files MLflow stored next to the model:", sorted(p.name for p in art_dir.iterdir()))
print((art_dir / "requirements.txt").read_text(encoding="utf-8").strip().splitlines()[:4], "...")
```
```text
reproduce the best run from MLflow: {'auc': (0.6917651585236163, 0.6917651585236163, True), 'accuracy': (0.7306666666666667, 0.7306666666666667, True)}
files MLflow stored next to the model: ['MLmodel', 'conda.yaml', 'input_example.json', 'model.pkl', 'python_env.yaml', 'requirements.txt', 'serving_input_example.json']
['mlflow==3.18.0', 'cloudpickle==3.1.2', 'numpy==2.5.4', 'pandas==3.1.1'] ...
```

**Question.** Your colleague logs `mlflow.log_param("seed", 0)` but the training script also shuffles with `np.random.shuffle` without a seed. The tracked run says `seed=0`. Is the run reproducible?

<details><summary>Answer</summary>

No. A tracked parameter only helps if the code actually *uses* it for every source of randomness. The record says `seed=0`, but the shuffle ignores it, so a rerun differs and the record is now misleading, which is worse than no record. The check is to run `reproduce` and compare the metrics: if they are not identical, the run is not reproducible, whatever the record claims. Make that check a test (section 8).

</details>

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw MLflow's two stores: a SQLite backend store holding a table of runs with columns (run_id, params, metrics, tags) and an artifact store folder holding for each run a model/ folder with MLmodel, model.pkl, requirements.txt, conda.yaml. Show a training script writing to both through start_run, log_params, log_metrics and log_model, and a browser UI plus a Python search_runs call reading from the backend store."

### 2.5 Try it

1. Add `mlflow.log_metric("auc", value, step=epoch)` inside a loop (for example a validation AUC after each of 50 boosting rounds using `staged_predict_proba`). How does `search_runs` show it differently from a single metric, and what does the UI draw?
2. Add the git commit hash as a tag. Why is a commit hash alone not enough when the working tree has uncommitted changes? (Hint: record `git diff` too, or refuse to run on a dirty tree.)
3. `mlflow.sklearn.autolog()` logs parameters and metrics with no extra lines. Name one thing it cannot know about your run that you must still log yourself.

## 3. Versioning data and pipelines with DVC

### 3.1 Why git is not enough

You already version code with git. Data and models are a different animal: large (megabytes to terabytes), binary, and usually changed wholesale. Git stores every version in full inside `.git`, so a 500 MB file edited ten times is 5 GB of history that everyone clones. The idea behind data versioning is simple and old: **content addressing**.

- Name a file by the **hash of its content**. Same content, same name; one changed byte, a new name.
- Keep the big files in a **store** (a folder, a shared disk, S3) under those names.
- Put a tiny **pointer** (the hash) in git. The git history of the pointer *is* the history of the data.

Eighteen lines of Python show the whole mechanism:

```python run
class ContentStore:
    """A content-addressed store: put(file) -> hash, get(hash, dest)."""
    def __init__(self, root): self.root = pathlib.Path(root); self.root.mkdir(parents=True, exist_ok=True)
    def put(self, path):
        h = hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()
        target = self.root / h[:2] / h[2:]
        if not target.exists():
            target.parent.mkdir(exist_ok=True); shutil.copy(path, target)       # same content twice is stored once
        return h
    def get(self, h, dest): shutil.copy(self.root / h[:2] / h[2:], dest)

store = ContentStore(ws / "toy_store")
data_v = ws / "toy_data.csv"
pointers = {}                                                                     # in real life: files tracked by git
for version, n in (("v1", 3000), ("v2", 4500)):
    make_customers(n, seed=1).to_csv(data_v, index=False)
    pointers[version] = store.put(data_v)
    print(f"{version}: {n} rows -> pointer {pointers[version][:12]}...  (a {len(pointers[version])}-character string goes into git)")
make_customers(3000, seed=1).to_csv(data_v, index=False)
print("saving identical v1 content again gives the same pointer:", store.put(data_v) == pointers["v1"],
      "| objects in the store:", sum(1 for _ in store.root.rglob('*') if _.is_file()))
store.get(pointers["v2"], data_v); print("restore v2 from its pointer:", len(pd.read_csv(data_v)), "rows")
store.get(pointers["v1"], data_v); print("restore v1 from its pointer:", len(pd.read_csv(data_v)), "rows")
```
```text
v1: 3000 rows -> pointer d69b3d277a05...  (a 64-character string goes into git)
v2: 4500 rows -> pointer e77762a121a2...  (a 64-character string goes into git)
saving identical v1 content again gives the same pointer: True | objects in the store: 2
restore v2 from its pointer: 4500 rows
restore v1 from its pointer: 3000 rows
```

**DVC** (Data Version Control) is this idea, done well: the pointer files are small `.dvc` text files, the store is a local cache plus a **remote** you push to and pull from, and it adds **pipelines** (stages with dependencies and outputs) so that `dvc repro` reruns only what changed.

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw git and DVC side by side. On the left, a git repository containing code and two tiny files customers.csv.dvc (each holding an md5 hash such as 8d304f85...). On the right, a storage box (remote) containing big objects named by their hashes. Arrows: 'dvc add' hashes the CSV and writes the pointer; 'dvc push' uploads the object; 'git checkout old-commit' then 'dvc checkout' fetches the old object back. Colour the pointers small and the objects large."

### 3.2 A real DVC session

We do it in a throw-away git repository inside the workspace. (DVC's anonymous usage analytics are switched off with an environment variable, and the commands print what they do.) Each step runs the real `git` and `dvc` programs and shows their real output:

```python run
VENV_BIN = pathlib.Path(sys.executable).parent
env = {**os.environ, "DVC_NO_ANALYTICS": "1", "PATH": f"{VENV_BIN}{os.pathsep}{os.environ['PATH']}", "GIT_AUTHOR_NAME": "tutorial", "GIT_AUTHOR_EMAIL": "t@example.com",
       "GIT_COMMITTER_NAME": "tutorial", "GIT_COMMITTER_EMAIL": "t@example.com", "NO_COLOR": "1"}
repo = ws / "dvc_demo"; repo.mkdir()

def sh(cmd, show=True, keep=None, cwd=None):
    r = subprocess.run(cmd, shell=True, cwd=cwd or repo, env=env, capture_output=True, text=True, encoding="utf-8")
    out = [l for l in (r.stdout + r.stderr).splitlines() if l.strip() and not set(l.strip()) <= set("|+-=")]
    if keep: out = [l for l in out if any(k in l for k in keep)]
    if show:
        print("$", cmd)
        for l in out[:14]: print("  " + l[:110])
    return r.returncode, "\n".join(out)

sh("git init -q . && git config core.autocrlf false && git branch -M main")
sh("dvc init", keep=["Initialized DVC repository"])
sh("dvc config core.analytics false", show=False)
(repo / "data").mkdir()
make_customers(4000, seed=0).to_csv(repo / "data" / "customers.csv", index=False)
sh("dvc add data/customers.csv")
print("\n--- data/customers.csv.dvc (this tiny file is what goes into git) ---"); print((repo / "data" / "customers.csv.dvc").read_text(encoding="utf-8").strip())
print("--- data/.gitignore (git must not see the big file) ---"); print((repo / "data" / ".gitignore").read_text(encoding="utf-8").strip())
sh("git add -A && git commit -q -m 'data v1: 4000 customers'", show=False)
print("\ngit sees:", sh("git log --oneline", show=False)[1])
```
```text
$ git init -q . && git config core.autocrlf false && git branch -M main
$ dvc init
  Initialized DVC repository.
$ dvc add data/customers.csv
  To track the changes with git, run:
  	git add data/.gitignore data/customers.csv.dvc
  To enable auto staging, run:
  	dvc config core.autostage true

--- data/customers.csv.dvc (this tiny file is what goes into git) ---
outs:
- md5: dfe7cc9a58bb57990f6f9de7daf5e41c
  size: 129238
  hash: md5
  path: customers.csv
--- data/.gitignore (git must not see the big file) ---
/customers.csv

git sees: a99e65b data v1: 4000 customers
```

The big CSV is invisible to git; only the 5-line pointer is committed. Next: a **remote** (a folder here, S3 or a shared disk in a team) and `push`:

```python run
sh("dvc remote add -d store ../dvc_remote")
sh("dvc push")
print("objects in the remote:", sorted(str(p.relative_to(ws / "dvc_remote")) for p in (ws / "dvc_remote").rglob("*") if p.is_file()))
sh("git add -A && git commit -q -m 'configure remote'", show=False)
```
```text
$ dvc remote add -d store ../dvc_remote
  Setting 'store' as a default remote.
$ dvc push
  1 file pushed
objects in the remote: ['files/md5/df/e7cc9a58bb57990f6f9de7daf5e41c']
```

Now the data **changes** (a new month of customers), we version it as v2, and then go back in time. Notice that two things move together: the *code history* in git and the *data history* it points to.

```python run
make_customers(6000, seed=0).to_csv(repo / "data" / "customers.csv", index=False)
sh("dvc status")
sh("dvc add data/customers.csv", show=False)
sh("git add -A && git commit -q -m 'data v2: 6000 customers'", show=False)
sh("dvc push", keep=["pushed"])
print("\nhistory:", sh("git log --oneline", show=False)[1].replace("\n", " | "))
print("rows now (v2):", len(pd.read_csv(repo / "data" / "customers.csv")))

v1_commit = sh("git log --format=%h --grep='data v1'", show=False)[1].strip()
sh(f"git checkout -q {v1_commit} -- data/customers.csv.dvc", show=False)                     # bring back the OLD pointer
sh("dvc checkout")                                                                           # make the file match the pointer
print("rows after going back to the data v1 pointer:", len(pd.read_csv(repo / "data" / "customers.csv")))
(repo / "data" / "customers.csv").unlink()
sh("git checkout -q main -- data/customers.csv.dvc", show=False)
sh("dvc pull")
print("deleted the file, pulled it from the remote; rows:", len(pd.read_csv(repo / "data" / "customers.csv")), "(v2 again)")
```
```text
$ dvc status
  data/customers.csv.dvc:
  	changed outs:
  		modified:           data/customers.csv
$ dvc push
  1 file pushed

history: ddde106 data v2: 6000 customers | 42bdd2b configure remote | a99e65b data v1: 4000 customers
rows now (v2): 6000
$ dvc checkout
  M       data/customers.csv
rows after going back to the data v1 pointer: 4000
$ dvc pull
  A       data/customers.csv
  1 file added
deleted the file, pulled it from the remote; rows: 6000 (v2 again)
```

### 3.3 Pipelines: only rerun what changed

A tracked file is a start; the real power is a **pipeline**: stages that declare their **dependencies** (code, data, parameters) and **outputs** (models, metrics). DVC stores a hash of everything in `dvc.lock`; if no dependency changed, the stage is skipped. We write the training script and its parameters (`params.yaml` is where tunable settings live, instead of being buried in code):

```python run
(repo / "params.yaml").write_text("seed: 0\nC: 1.0\ntest_size: 0.25\n", encoding="utf-8")
(repo / "train.py").write_text('''import json, yaml, joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

p = yaml.safe_load(open("params.yaml", encoding="utf-8"))
df = pd.read_csv("data/customers.csv")
NUM, CAT = ["tenure_months", "monthly_spend", "support_tickets"], ["plan", "region"]
tr, te = train_test_split(df, test_size=p["test_size"], random_state=p["seed"], stratify=df["churned"])
pipe = Pipeline([("prep", ColumnTransformer([("num", StandardScaler(), NUM), ("cat", OneHotEncoder(handle_unknown="ignore"), CAT)])),
                 ("model", LogisticRegression(C=p["C"], max_iter=1000))]).fit(tr[NUM + CAT], tr["churned"])
joblib.dump(pipe, "model.joblib")
json.dump({"auc": round(roc_auc_score(te["churned"], pipe.predict_proba(te[NUM + CAT])[:, 1]), 5), "rows": len(df)}, open("metrics.json", "w", encoding="utf-8"))
''', encoding="utf-8")
sh(f'dvc stage add -n train -d train.py -d data/customers.csv -p seed,C,test_size -o model.joblib -M metrics.json "python train.py"', show=False)
print("--- dvc.yaml ---"); print((repo / "dvc.yaml").read_text(encoding="utf-8").strip())
print("\n--- first dvc repro ---")
sh("dvc repro", keep=["Running stage", "Updating lock", "python train.py", "Use `dvc push`", "Stage"])
print("metrics:", (repo / "metrics.json").read_text(encoding="utf-8").strip())
print("\n--- second dvc repro, nothing changed ---")
sh("dvc repro", keep=["Stage", "up to date", "didn't change", "Data and pipelines"])
```
```text
--- dvc.yaml ---
stages:
  train:
    cmd: python train.py
    deps:
    - data/customers.csv
    - train.py
    params:
    - C
    - seed
    - test_size
    outs:
    - model.joblib
    metrics:
    - metrics.json:
        cache: false

--- first dvc repro ---
$ dvc repro
  Running stage 'train':
  > python train.py
  Updating lock file 'dvc.lock'
  Use `dvc push` to send your updates to remote storage.
metrics: {"auc": 0.69055, "rows": 6000}

--- second dvc repro, nothing changed ---
$ dvc repro
  'data/customers.csv.dvc' didn't change, skipping
  Stage 'train' didn't change, skipping
  Data and pipelines are up to date.
```

Now change one parameter. Only the stage that depends on it reruns, and DVC can tell you exactly what changed in parameters and in metrics between the workspace and the last commit:

```python run
sh("git add -A && git commit -q -m 'pipeline with C=1.0'", show=False)
(repo / "params.yaml").write_text("seed: 0\nC: 0.05\ntest_size: 0.25\n", encoding="utf-8")
print("--- dvc repro after changing C from 1.0 to 0.05 ---")
sh("dvc repro", keep=["Running stage", "Updating lock", "python train.py"])
sh("dvc params diff")
sh("dvc metrics diff")
```
```text
--- dvc repro after changing C from 1.0 to 0.05 ---
$ dvc repro
  Running stage 'train':
  > python train.py
  Updating lock file 'dvc.lock'
$ dvc params diff
  Path         Param    HEAD    workspace
  params.yaml  C        1.0     0.05
$ dvc metrics diff
  Path          Metric    HEAD     workspace    Change
  metrics.json  auc       0.69055  0.69177      0.00122
```

`dvc.lock` records the hash of every dependency and output, so a colleague who checks out your commit and runs `dvc pull` gets *your* data and model, and `dvc repro` rebuilds only what is stale. Together with MLflow this answers the syllabus outcome: the tracked config (`params.yaml` in git), the data pointer (`.dvc` in git) and the code (git) fix a run completely.

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw a DVC pipeline as a small graph: inputs data/customers.csv, train.py and params.yaml (seed, C, test_size) feed one stage called train, which outputs model.joblib and metrics.json. Show two runs. Run 1: everything stale, the stage runs. Run 2: nothing changed, the stage is greyed out with the label 'skipped, hashes match dvc.lock'. Run 3: C changed from 1.0 to 0.05, only the train box lights up. Show metrics.json auc before and after: 0.6891 then 0.6893."

**Question.** Your teammate edits `train.py` by adding a comment only (no logic change) and runs `dvc repro`. Does the stage rerun? What about a change in `README.md`?

<details><summary>Answer</summary>

Yes to the comment: DVC hashes the *file contents*, so any change to a declared dependency, even a comment, marks the stage stale and reruns it (this is the safe default; the cost is an occasional unnecessary run). No to `README.md`: it is not declared as a dependency of any stage, so DVC ignores it. This is why you must declare every file the stage reads (`-d`) and every setting it uses (`-p`); an undeclared dependency changes results without triggering a rerun, which is a silent reproducibility bug.

</details>

### 3.4 DVC cheat sheet and common errors

| Task | Command |
|---|---|
| start in a git repo | `dvc init` then commit `.dvc/` |
| track a file or folder | `dvc add data/x.csv` then `git add data/x.csv.dvc data/.gitignore` |
| set up storage | `dvc remote add -d name /path/or/s3://bucket/path` |
| upload / download | `dvc push` / `dvc pull` |
| make files match the pointers in git | `dvc checkout` |
| what is out of date | `dvc status` |
| define a stage | `dvc stage add -n name -d dep -p param -o out -M metrics.json "cmd"` |
| run the pipeline | `dvc repro` (reruns stale stages only) |
| compare experiments | `dvc params diff`, `dvc metrics diff` |

| Error | Cause and fix |
|---|---|
| `ERROR: output 'x.csv' is already tracked by SCM (e.g. Git)` | the file was committed to git before; `git rm --cached x.csv` first, then `dvc add` |
| `failed to pull data from the cloud` / missing cache | someone forgot `dvc push`; ask them to push, or `dvc fetch` from the right remote |
| stage reruns every time | an output or dependency changes on each run (a timestamp in a file, an unseeded model); make the stage deterministic |
| `stage 'train' is not up to date` after switching branches | run `dvc checkout`, then `dvc repro` |

## 4. The model registry and promotion gates

### 4.1 A registry is a name, versions and labels

A model file lying in a run folder is not something a service should load. A **model registry** gives a model a stable *name*, numbered *versions*, and **aliases** (movable labels such as `champion`: the version that serves real traffic). The serving code asks for `churn-model@champion` and never mentions a file path or run id, so **promoting and rolling back are just moving a label**.

```python run
from mlflow import MlflowClient
client = MlflowClient()
NAME = "churn-model"
v_logreg = mlflow.register_model(f"runs:/{run_ids[1]}/model", NAME)             # the best run (logreg, C=0.05)
v_gbm = mlflow.register_model(f"runs:/{run_ids[3]}/model", NAME)                # the deepest GBM
client.set_registered_model_alias(NAME, "champion", v_logreg.version)
client.set_registered_model_alias(NAME, "challenger", v_gbm.version)
client.set_model_version_tag(NAME, v_logreg.version, "validated", "holdout-999")
aliases = client.get_registered_model(NAME).aliases                                   # {alias: version}
rows = [{"version": v.version, "aliases": sorted(a for a, ver in aliases.items() if ver == v.version), "from run": mlflow.get_run(v.run_id).data.tags["mlflow.runName"], "tags": dict(v.tags)}
        for v in client.search_model_versions(f"name='{NAME}'")]
print(pd.DataFrame(rows).sort_values("version").to_string(index=False))
champion = mlflow.sklearn.load_model(f"models:/{NAME}@champion")
print("serving code loads 'models:/churn-model@champion' ->", type(champion.named_steps["model"]).__name__)
```
```text
 version      aliases from run                         tags
       1   [champion] logreg-1 {'validated': 'holdout-999'}
       2 [challenger]    gbm-3                           {}
serving code loads 'models:/churn-model@champion' -> LogisticRegression
```

### 4.2 The gate: should the challenger replace the champion?

Never promote because "the AUC is higher by 0.003". Compare both models on a **holdout set that was never used for any decision**, put an **interval** on the difference (a paired bootstrap over the same rows, as in ml.05), and add **guardrails** that are not accuracy: calibration, latency, behaviour on important groups.

```python run
from sklearn.metrics import roc_auc_score
holdout = make_customers(5000, seed=999)
y_h = holdout[TARGET].to_numpy()

def auc_gain(y, p_champ, p_cand, n_boot=600, seed=0):
    rng = np.random.default_rng(seed); gains = []
    for _ in range(n_boot):
        idx = rng.integers(0, len(y), len(y))
        gains.append(roc_auc_score(y[idx], p_cand[idx]) - roc_auc_score(y[idx], p_champ[idx]))
    return float(np.mean(gains)), np.percentile(gains, [2.5, 97.5])

def ece(y, p, bins=10):
    edges = np.linspace(0, 1, bins + 1); idx = np.clip(np.digitize(p, edges) - 1, 0, bins - 1); e = 0.0
    for b in range(bins):
        if (idx == b).any(): e += (idx == b).mean() * abs(p[idx == b].mean() - y[idx == b].mean())
    return e

def p95_latency_ms(model, X, reps=15, batch=200):
    ts = []
    for _ in range(reps):
        t0 = time.perf_counter(); model.predict_proba(X.head(batch)); ts.append((time.perf_counter() - t0) * 1000)
    return float(np.percentile(ts, 95))

def gate(champ, cand, X, y, min_gain=0.0, max_ece=0.05, max_latency_ms=50.0):
    pc, pn = champ.predict_proba(X)[:, 1], cand.predict_proba(X)[:, 1]
    gain, (lo, hi) = auc_gain(y, pc, pn)
    checks = {"AUC gain (mean)": round(gain, 4), "gain 95% interval": f"[{lo:+.4f}, {hi:+.4f}]", "interval lower bound > min_gain": lo > min_gain,
              "candidate ECE": round(ece(y, pn), 4), "ECE ok": ece(y, pn) <= max_ece,
              "candidate p95 latency ms": round(p95_latency_ms(cand, X), 1), "latency ok": p95_latency_ms(cand, X) <= max_latency_ms}
    checks["PROMOTE"] = bool(checks["interval lower bound > min_gain"] and checks["ECE ok"] and checks["latency ok"])
    return checks

challenger = mlflow.sklearn.load_model(f"models:/{NAME}@challenger")
big = make_customers(30000, seed=5)
def fit_logreg(d): return Pipeline([("prep", preprocess()), ("model", LogisticRegression(C=0.05, max_iter=1000))]).fit(d[NUM + CAT], d[TARGET])
stale = fit_logreg(big.head(60))                                     # a launch-day model trained on only 60 customers
retrained = fit_logreg(big)                                          # the same model class retrained on 30,000 customers
scenarios = {"GBM (depth 3, 200 trees) vs champion": (champion, challenger),
             "champion retrained on 30,000 vs champion": (champion, retrained),
             "retrained on 30,000 vs a STALE model (60 rows)": (stale, retrained)}
rows = []
for label, (a_, b_) in scenarios.items():
    g = gate(a_, b_, holdout[NUM + CAT], y_h)
    rows.append([label, g["AUC gain (mean)"], g["gain 95% interval"], g["candidate ECE"], g["candidate p95 latency ms"], "YES" if g["PROMOTE"] else "no"])
print(pd.DataFrame(rows, columns=["challenger against champion", "AUC gain", "95% interval", "ECE", "p95 ms", "promote?"]).to_string(index=False))
```
```text
                   challenger against champion  AUC gain       95% interval    ECE  p95 ms promote?
          GBM (depth 3, 200 trees) vs champion   -0.0217 [-0.0298, -0.0140] 0.0327     4.7       no
      champion retrained on 30,000 vs champion    0.0009 [-0.0012, +0.0033] 0.0126     4.1       no
retrained on 30,000 vs a STALE model (60 rows)    0.0155 [+0.0074, +0.0238] 0.0126     3.9      YES
```

Three different stories in one table. The deeper GBM is *worse* than the champion (the interval is entirely below zero), so no. Retraining the same model on 30,000 customers instead of 4,500 changes almost nothing (the interval straddles zero), so no: this model class had already learned what the data can teach, which is a useful thing to know before paying for a retraining pipeline. Only the challenger that is clearly better than a stale incumbent passes (interval entirely above zero), and the data here are generated, so you can check that verdict against the truth.

Read the interval, not only the verdict: whether more data helps enough to clear a gate depends on how much signal is left to learn. If the lower bound is below zero, the right action is "no evidence of improvement", not "promote and see". When the gate says yes, promotion is one line, and so is the rollback:

```python run
client.set_registered_model_alias(NAME, "champion", v_gbm.version)                 # PROMOTE (pretend): the alias moves, nothing is copied
print("after promotion  : champion is now", client.get_model_version_by_alias(NAME, "champion").version, "(version", v_gbm.version, "= GBM)")
client.set_registered_model_alias(NAME, "champion", v_logreg.version)              # ROLLBACK: move it back
print("after rollback   : champion is now", client.get_model_version_by_alias(NAME, "champion").version, "(version", v_logreg.version, "= logistic regression)")
```
```text
after promotion  : champion is now 2 (version 2 = GBM)
after rollback   : champion is now 1 (version 1 = logistic regression)
```

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw a model registry named churn-model with version 1 (logistic regression) and version 2 (gradient boosting) as two cards. Draw two movable labels, champion and challenger, as flags attached to the cards. Show a serving box that always asks for churn-model@champion. Animate promotion (the champion flag jumps from v1 to v2) and rollback (it jumps back), and show that the serving code never changes."

### 4.3 Releasing safely: shadow, canary, rollback

Even a model that passes the gate can behave differently on live traffic. Three standard release patterns, from safest to riskiest:

| Pattern | What happens | What you learn | Risk to users |
|---|---|---|---|
| **Shadow** | the new model receives a copy of every request; its answers are logged, never returned | agreement with the champion, latency, errors on real inputs | none |
| **Canary** | a small share (say 5%) of requests get the new model's answers | real outcomes on a slice, before a full rollout | small, bounded |
| **Blue/green + rollback** | two full environments; switch traffic at once; switch back if alarms fire | nothing until the switch | all or nothing, fast undo |

A canary needs a **sticky, deterministic split**: the same customer must always get the same model (otherwise one person sees two behaviours), and the split must be reproducible. Hash the id with a salt:

```python run
def bucket(customer_id, salt="churn-canary-1"):
    return int(hashlib.sha256(f"{salt}:{customer_id}".encode()).hexdigest()[:8], 16) % 100          # 0..99

ids = np.arange(100_000)
b = np.array([bucket(i) for i in ids])
print("share routed to the canary (bucket < 5):", round(float((b < 5).mean()), 4), "| first ids:", [(i, bucket(i)) for i in range(5)])
print("sticky: same id, same bucket on every call:", all(bucket(i) == bucket(i) for i in range(1000)))
b2 = np.array([bucket(i, salt="churn-canary-2") for i in ids])
print("a new salt reshuffles: share of customers in the canary under BOTH salts:", round(float(((b < 5) & (b2 < 5)).mean()), 4), "(about 0.05 x 0.05 = 0.0025 if independent)")
print("raising the canary to 25% keeps everyone who was already in it:", bool(((b < 5) <= (b < 25)).all()))
```
```text
share routed to the canary (bucket < 5): 0.0502 | first ids: [(0, 81), (1, 21), (2, 93), (3, 0), (4, 53)]
sticky: same id, same bucket on every call: True
a new salt reshuffles: share of customers in the canary under BOTH salts: 0.0025 (about 0.05 x 0.05 = 0.0025 if independent)
raising the canary to 25% keeps everyone who was already in it: True
```

**Question.** The canary's AUC on the first day is 0.62, the champion's is 0.68. Roll back?

<details><summary>Answer</summary>

Not on that number alone. A 5% slice of one day might hold only a few hundred customers, and with delayed labels (most churners have not churned *yet*) the AUC of a day-one canary is mostly noise and survivorship. Decide the evidence you need **before** the release: guardrails you can measure immediately (error rate, latency, prediction distribution compared with the champion on the same requests, as in shadow mode), and a performance comparison only after enough labelled outcomes arrive, with an interval. Roll back at once for hard failures (errors, impossible predictions, latency); wait for the interval on performance.

</details>

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Animate a canary release with 100 buckets drawn as a 10 by 10 grid of squares. Each request carries a customer id that is hashed to a bucket from 0 to 99. Buckets 0 to 4 are coloured orange (canary model) and the rest blue (champion model). Show the same customer id landing in the same square every time, then widen the canary to 25 squares keeping the first 5 orange. Add a panel with the canary's error rate and latency next to the champion's."

### 4.4 Try it

1. Register a third version (logistic regression with `C=10`) and give it the alias `shadow`. Write the code that loads `@champion` and `@shadow`, scores a batch with both, and prints the share of customers where they disagree on the predicted class.
2. Add a fairness-style guardrail to `gate`: the candidate's AUC on each `region` must not fall below the champion's by more than 0.03. What is the risk of checking many slices at once? (ds.09: multiple comparisons.)
3. Tag each registered version with the DVC data hash (`git rev-parse HEAD` and the `.dvc` md5). Why does the registry then answer "which data trained the model in production?"

## 5. Serving a model: FastAPI, then Docker

### 5.1 What "serving" means

A model in a notebook answers *you*. A served model answers *other programs*, many times a second, for months. That changes what matters:

| Concern | Question to answer |
|---|---|
| **Contract** | exactly which fields come in, with which types and ranges? what comes out? |
| **Load once** | the model is read from disk at startup, not on every request |
| **Latency and batching** | one request at a time, or 200 rows in one call? |
| **Identity** | which model version produced this answer? (return it in every response) |
| **Health** | can a load balancer ask "are you alive and is a model loaded?" |
| **Logging** | every prediction is recorded (inputs, score, version): monitoring (section 7) needs it |
| **Environment** | the same library versions as training, or the pickle may break or give different numbers |

We serve with **FastAPI** (you met it in swe.05): request and response models give the contract and validation for free. First, export the champion from the registry as a small, self-describing **model folder**: the pipeline file plus a `meta.json` of facts the service should expose.

```python run
svc = ws / "service"; (svc / "model").mkdir(parents=True)
champ_version = client.get_model_version_by_alias(NAME, "champion")
joblib.dump(champion, svc / "model" / "model.joblib")
meta = {"model_name": NAME, "model_version": f"v{champ_version.version}", "mlflow_run_id": champ_version.run_id,
        "data_sha256": file_sha256(data_file), "trained_with": {"scikit-learn": sklearn.__version__, "numpy": np.__version__, "python": platform.python_version()},
        "features": NUM + CAT, "decision_threshold": 0.5}
(svc / "model" / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
print(json.dumps({k: v for k, v in meta.items() if k != "mlflow_run_id"}, indent=1)[:700], "...")
print("model file:", round((svc / "model" / "model.joblib").stat().st_size / 1024, 1), "KB")
```
```text
{
 "model_name": "churn-model",
 "model_version": "v1",
 "data_sha256": "fdd7ed8b31aec4de",
 "trained_with": {
  "scikit-learn": "1.9.1",
  "numpy": "2.5.4",
  "python": "3.14.4"
 },
 "features": [
  "tenure_months",
  "monthly_spend",
  "support_tickets",
  "plan",
  "region"
 ],
 "decision_threshold": 0.5
} ...
model file: 3.5 KB
```

### 5.2 The service

The whole service is one file. Read it top to bottom: configuration from environment variables, the **contract** (`Customer`: types, ranges, allowed categories), the model loaded **once** at import, `/health`, `/metadata`, `/predict`, `/predict/batch`, and one JSON line appended to a prediction log for every scored customer. Counters and a latency histogram are kept in memory and exposed on `/metrics` (we use them in section 7).

```python run
(svc / "churn_service.py").write_text('''"""churn_service: a small model-serving API (FastAPI)."""
import json, os, time, uuid, threading
from pathlib import Path
from typing import Literal

import joblib
import pandas as pd
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field

MODEL_DIR = Path(os.environ.get("MODEL_DIR", Path(__file__).parent / "model"))
PRED_LOG = Path(os.environ.get("PRED_LOG", MODEL_DIR.parent / "predictions.jsonl"))

model = joblib.load(MODEL_DIR / "model.joblib")                 # loaded ONCE, when the process starts
meta = json.loads((MODEL_DIR / "meta.json").read_text(encoding="utf-8"))
COLUMNS = meta["features"]
_lock = threading.Lock()


class Customer(BaseModel):
    """The input contract. Anything outside it is rejected with HTTP 422 before it reaches the model."""
    tenure_months: float = Field(ge=0, le=600)
    monthly_spend: float = Field(ge=0, le=10_000)
    support_tickets: int = Field(ge=0, le=500)
    plan: Literal["basic", "standard", "premium"]
    region: Literal["north", "south", "east", "west"]


class BatchRequest(BaseModel):
    customers: list[Customer] = Field(min_length=1, max_length=1000)


app = FastAPI(title="churn-service", version=meta["model_version"])
BUCKETS = [5, 10, 25, 50, 100, 250, 1000]                        # latency histogram, milliseconds
STATS = {"requests": 0, "errors": 0, "predictions": 0, "lat_sum": 0.0, "lat_buckets": [0] * len(BUCKETS), "lat_count": 0}


def _record_latency(ms):
    with _lock:
        STATS["lat_sum"] += ms; STATS["lat_count"] += 1
        for i, b in enumerate(BUCKETS):
            if ms <= b: STATS["lat_buckets"][i] += 1; break          # count in the FIRST bucket that fits; /metrics makes them cumulative


def _score(customers):
    t0 = time.perf_counter()
    frame = pd.DataFrame([c.model_dump() for c in customers])[COLUMNS]
    probs = model.predict_proba(frame)[:, 1]
    request_id = uuid.uuid4().hex[:12]
    with _lock, open(PRED_LOG, "a", encoding="utf-8") as f:                       # one line per scored customer: the raw material for monitoring
        for c, p in zip(customers, probs):
            f.write(json.dumps({"ts": time.time(), "request_id": request_id, "model_version": meta["model_version"], "score": round(float(p), 6), **c.model_dump()}) + "\\n")
    ms = (time.perf_counter() - t0) * 1000
    with _lock:
        STATS["requests"] += 1; STATS["predictions"] += len(customers)
    _record_latency(ms)
    return request_id, probs


@app.get("/health")
def health():
    return {"status": "ok", "model_version": meta["model_version"]}


@app.get("/metadata")
def metadata():
    return meta


@app.post("/predict")
def predict(customer: Customer):
    request_id, probs = _score([customer])
    p = float(probs[0])
    return {"request_id": request_id, "model_version": meta["model_version"], "churn_probability": round(p, 6), "will_churn": p >= meta["decision_threshold"]}


@app.post("/predict/batch")
def predict_batch(req: BatchRequest):
    request_id, probs = _score(req.customers)
    return {"request_id": request_id, "model_version": meta["model_version"], "churn_probability": [round(float(p), 6) for p in probs]}


@app.get("/metrics", response_class=PlainTextResponse)
def metrics():
    s, lines = STATS, []
    lines += ["# TYPE churn_requests_total counter", f"churn_requests_total {s['requests']}"]
    lines += ["# TYPE churn_predictions_total counter", f"churn_predictions_total {s['predictions']}"]
    lines += ["# TYPE churn_request_latency_ms histogram"]
    cum = 0
    for b, c in zip(BUCKETS, s["lat_buckets"]):
        cum += c; lines.append(f'churn_request_latency_ms_bucket{{le="{b}"}} {cum}')
    lines += [f'churn_request_latency_ms_bucket{{le="+Inf"}} {s["lat_count"]}', f"churn_request_latency_ms_sum {s['lat_sum']:.3f}", f"churn_request_latency_ms_count {s['lat_count']}"]
    return "\\n".join(lines) + "\\n"
''', encoding="utf-8")
print("wrote", (svc / "churn_service.py").name, "-", len((svc / "churn_service.py").read_text(encoding="utf-8").splitlines()), "lines")
```
```text
wrote churn_service.py - 94 lines
```

FastAPI ships a test client that calls the app **in-process** (no network), which is the right way to unit-test the contract. Valid requests, then invalid ones:

```python run
os.environ["MODEL_DIR"] = str(svc / "model"); os.environ["PRED_LOG"] = str(ws / "predictions_test.jsonl")
sys.path.insert(0, str(svc))
import importlib, churn_service
from fastapi.testclient import TestClient
api = TestClient(churn_service.app)

good = {"tenure_months": 8.5, "monthly_spend": 47.0, "support_tickets": 4, "plan": "standard", "region": "north"}
print("GET /health   ->", api.get("/health").json())
r = api.post("/predict", json=good); print("POST /predict ->", r.status_code, r.json())
rows = holdout[NUM + CAT].head(3).to_dict("records")
print("POST /predict/batch (3 customers) ->", api.post("/predict/batch", json={"customers": rows}).json())
print("\ninvalid requests are rejected BEFORE the model sees them:")
for label, bad in [("unknown plan 'gold'", {**good, "plan": "gold"}), ("negative tenure", {**good, "tenure_months": -3}), ("missing field", {k: v for k, v in good.items() if k != "region"}),
                   ("text where a number belongs", {**good, "monthly_spend": "lots"})]:
    r = api.post("/predict", json=bad); e = r.json()["detail"][0]
    print(f"  {label:<30} -> {r.status_code}  {e['loc'][-1]}: {e['msg']}")
```
```text
GET /health   -> {'status': 'ok', 'model_version': 'v1'}
POST /predict -> 200 {'request_id': 'da38dcaf184e', 'model_version': 'v1', 'churn_probability': 0.718976, 'will_churn': True}
POST /predict/batch (3 customers) -> {'request_id': '67e9991461a5', 'model_version': 'v1', 'churn_probability': [0.197313, 0.49844, 0.339203]}

invalid requests are rejected BEFORE the model sees them:
  unknown plan 'gold'            -> 422  plan: Input should be 'basic', 'standard' or 'premium'
  negative tenure                -> 422  tenure_months: Input should be greater than or equal to 0
  missing field                  -> 422  region: Field required
  text where a number belongs    -> 422  monthly_spend: Input should be a valid number, unable to parse string as a number
```

**Batching.** One call that carries 200 customers is far cheaper than 200 calls, because the model's cost is dominated by fixed overhead per call (building the frame, the pipeline's steps, the HTTP round trip). Measured in-process, the batch advantage is already large; over a real network it is larger:

```python run
rows200 = holdout[NUM + CAT].head(200).to_dict("records")
t0 = time.perf_counter()
for row in rows200: api.post("/predict", json=row)
t_single = (time.perf_counter() - t0) * 1000
t0 = time.perf_counter(); api.post("/predict/batch", json={"customers": rows200}); t_batch = (time.perf_counter() - t0) * 1000
print(f"200 single calls: {t_single:7.0f} ms total ({t_single / 200:5.2f} ms per customer)")
print(f"1 batch of 200  : {t_batch:7.0f} ms total ({t_batch / 200:5.2f} ms per customer)  -> {t_single / t_batch:.0f}x less time per customer")
```
```text
200 single calls:    2269 ms total (11.34 ms per customer)
1 batch of 200  :      17 ms total ( 0.09 ms per customer)  -> 130x less time per customer
```

Now a **real** server: `uvicorn` in a separate process on `127.0.0.1`, called over actual HTTP. This is what the container will run, so we check it works outside the test client:

```python run
import httpx
port = 18080
srv_env = {**os.environ, "MODEL_DIR": str(svc / "model"), "PRED_LOG": str(ws / "predictions_uvicorn.jsonl")}
proc = subprocess.Popen([sys.executable, "-m", "uvicorn", "churn_service:app", "--app-dir", str(svc), "--host", "127.0.0.1", "--port", str(port), "--log-level", "warning"],
                        env=srv_env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
try:
    for _ in range(80):
        try: httpx.get(f"http://127.0.0.1:{port}/health", timeout=0.5).raise_for_status(); break
        except Exception: time.sleep(0.25)
    print("server up:", httpx.get(f"http://127.0.0.1:{port}/health").json())
    lat = []
    with httpx.Client(base_url=f"http://127.0.0.1:{port}") as http:
        for row in rows200[:100]:
            t0 = time.perf_counter(); http.post("/predict", json=row); lat.append((time.perf_counter() - t0) * 1000)
    print(f"100 sequential HTTP requests: median {np.median(lat):.1f} ms, p95 {np.percentile(lat, 95):.1f} ms")
    same = httpx.post(f"http://127.0.0.1:{port}/predict", json=good).json()["churn_probability"]
    print("HTTP answer equals the in-process answer:", same == api.post("/predict", json=good).json()["churn_probability"])
finally:
    proc.terminate(); proc.wait(timeout=10)
print("server stopped, exit code", proc.returncode)
```
```text
server up: {'status': 'ok', 'model_version': 'v1'}
100 sequential HTTP requests: median 5.3 ms, p95 7.5 ms
HTTP answer equals the in-process answer: True
server stopped, exit code -15
```

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw the lifecycle of one request to the churn service: a JSON body arrives, the Customer contract checks types and ranges (green tick or a red 422 branch for plan='gold'), the values become a one-row DataFrame, the preloaded model scores it, one JSON line is appended to predictions.jsonl, and a response with request_id, model_version and churn_probability is returned. Show the model file being loaded once at startup, not per request, and a second arrow for GET /health."

### 5.3 The model's environment: a Docker image

The service works here because this machine has the right Python and scikit-learn. On a server it must be **the same environment**, and Docker packages the environment with the code. The recipe, a `Dockerfile`, has the shape you know from swe.09, with the points that matter for ML:

- **Pin the library versions to the ones used for training** (`requirements.txt` generated from the training environment). A model pickled with one scikit-learn version may fail to load, or silently differ, under another.
- **Build from wheels you already downloaded** (`pip install --no-index --find-links=/wheels`). Besides being fast, the build then needs no network and cannot pick up a different version of anything: a *hermetic* build. (On the machine where this chapter was run, `pip install` from inside a container was so slow that downloading even NumPy took four minutes; pre-downloading on the host took two seconds. If your Docker builds crawl, that is the first thing to try.)
- Copy the model folder **into** the image (the image is the deployable unit) or mount it; here we copy it.
- Run as a **non-root** user; add a `HEALTHCHECK`; install without cache to keep the image small.

```python run
ctx = ws / "docker_ctx"; (ctx / "service").mkdir(parents=True)
shutil.copytree(svc / "model", ctx / "service" / "model"); shutil.copy(svc / "churn_service.py", ctx / "service" / "churn_service.py")
import fastapi, uvicorn, pydantic
pins = {"fastapi": fastapi.__version__, "uvicorn": uvicorn.__version__, "pydantic": pydantic.__version__, "scikit-learn": sklearn.__version__,
        "numpy": np.__version__, "pandas": pd.__version__, "joblib": joblib.__version__, "scipy": scipy.__version__}
(ctx / "requirements.txt").write_text("\n".join(f"{k}=={v}" for k, v in pins.items()) + "\n", encoding="utf-8")

# Download the exact wheels ONCE, on the host, for the container's platform (Linux, Python 3.14). The image is then built from these files, offline.
t0 = time.time()
r = subprocess.run([sys.executable, "-m", "pip", "download", "-q", "-r", str(ctx / "requirements.txt"), "-d", str(ctx / "wheels"), "--only-binary=:all:", "--python-version", "3.14", "--implementation", "cp",
                    "--platform", "manylinux_2_28_x86_64", "--platform", "manylinux2014_x86_64", "--platform", "manylinux_2_17_x86_64", "--platform", "any"], capture_output=True, text=True, encoding="utf-8")
wheels = sorted((ctx / "wheels").glob("*.whl"))
print(f"pip download: exit code {r.returncode}, {len(wheels)} wheels, {sum(w.stat().st_size for w in wheels) / 1e6:.0f} MB, {time.time() - t0:.0f}s")
(ctx / "Dockerfile").write_text('''FROM python:3.14-slim
WORKDIR /srv
COPY requirements.txt .
COPY wheels /wheels
RUN pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt
COPY service/ /srv/
RUN useradd --create-home app && chown -R app /srv
USER app
ENV MODEL_DIR=/srv/model PRED_LOG=/srv/predictions.jsonl
EXPOSE 8000
HEALTHCHECK --interval=10s --timeout=3s CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health').status==200 else 1)"
CMD ["uvicorn", "churn_service:app", "--host", "0.0.0.0", "--port", "8000"]
''', encoding="utf-8")
print((ctx / "requirements.txt").read_text(encoding="utf-8").strip().replace("\n", "  "))
print("\n" + (ctx / "Dockerfile").read_text(encoding="utf-8").strip())
```
```text
pip download: exit code 0, 24 wheels, 78 MB, 2s
fastapi==0.162.0  uvicorn==0.54.0  pydantic==2.14.3  scikit-learn==1.9.1  numpy==2.5.4  pandas==3.1.1  joblib==1.6.0  scipy==1.18.1

FROM python:3.14-slim
WORKDIR /srv
COPY requirements.txt .
COPY wheels /wheels
RUN pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt
COPY service/ /srv/
RUN useradd --create-home app && chown -R app /srv
USER app
ENV MODEL_DIR=/srv/model PRED_LOG=/srv/predictions.jsonl
EXPOSE 8000
HEALTHCHECK --interval=10s --timeout=3s CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health').status==200 else 1)"
CMD ["uvicorn", "churn_service:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run it. **What this does on your machine:** it uses the `python:3.14-slim` base image (pulled once, about 45 MB compressed), installs the pre-downloaded wheels (no network), then starts **one** container named `pbtut-churn` bound to `127.0.0.1:18081` only, and at the end removes that container and that image. Nothing else on the machine is touched.

```python run
def docker(args, show=True, tail=8):
    r = subprocess.run(["docker"] + args, capture_output=True, text=True, encoding="utf-8")
    out = [l for l in (r.stdout + r.stderr).splitlines() if l.strip()]
    if show:
        print("$ docker " + " ".join(args)); [print("  " + l[:120]) for l in out[-tail:]]
    return r.returncode, "\n".join(out)

docker_ok = shutil.which("docker") is not None and docker(["info", "--format", "{{.ServerVersion}}"], show=False)[0] == 0
if not docker_ok:
    print("Docker is not available on this machine: skip this section, the rest of the chapter does not depend on it.")
else:
    t0 = time.time()
    rc, out = docker(["build", "--progress=plain", "-t", "pbtut-churn:1", str(ctx)], show=False)
    print(f"docker build: exit code {rc}, {time.time() - t0:.0f}s")
    for l in out.splitlines():
        if "naming to" in l or "exporting to image" in l and "done" in l.lower(): print("  " + l.strip()[:110])
    docker(["image", "ls", "pbtut-churn", "--format", "table {{.Repository}}:{{.Tag}}\t{{.Size}}"])
```
```text
docker build: exit code 0, 4s
  #12 naming to docker.io/library/pbtut-churn:1 done
$ docker image ls pbtut-churn --format table {{.Repository}}:{{.Tag}}	{{.Size}}
  REPOSITORY:TAG   SIZE
  pbtut-churn:1    849MB
```

```python run
if docker_ok:
    docker(["run", "-d", "--name", "pbtut-churn", "-p", "127.0.0.1:18081:8000", "pbtut-churn:1"], tail=1)
    try:
        for _ in range(120):
            try: httpx.get("http://127.0.0.1:18081/health", timeout=0.5).raise_for_status(); break
            except Exception: time.sleep(0.5)
        print("container health endpoint:", httpx.get("http://127.0.0.1:18081/health").json())
        in_container = httpx.post("http://127.0.0.1:18081/predict", json=good).json()["churn_probability"]
        print(f"prediction from the container {in_container} | from the local test client {api.post('/predict', json=good).json()['churn_probability']} | identical:",
              in_container == api.post("/predict", json=good).json()["churn_probability"])
        print("container user:", docker(["exec", "pbtut-churn", "whoami"], show=False)[1], "| python inside:", docker(["exec", "pbtut-churn", "python", "--version"], show=False)[1])
        rc, logs = docker(["logs", "pbtut-churn"], show=False); print("container log tail:", logs.splitlines()[-2:] if logs else "(empty)")
        for _ in range(40):
            health = docker(["inspect", "-f", "{{.State.Health.Status}}", "pbtut-churn"], show=False)[1]
            if health == "healthy": break
            time.sleep(1)
        print("health status as Docker sees it (from the HEALTHCHECK in the Dockerfile):", health)
    finally:
        docker(["rm", "-f", "pbtut-churn"], tail=1); docker(["rmi", "pbtut-churn:1"], show=False)
        print("cleaned up: my container and my image removed; yours untouched ->", docker(["ps", "--format", "{{.Names}}"], show=False)[1].split())
```
```text
$ docker run -d --name pbtut-churn -p 127.0.0.1:18081:8000 pbtut-churn:1
  aa1fb31381035855526fe39cf2f144682608a23a3a419a297fe9db091f1f0c8b
container health endpoint: {'status': 'ok', 'model_version': 'v1'}
prediction from the container 0.718976 | from the local test client 0.718976 | identical: True
container user: app | python inside: Python 3.14.10
container log tail: ['INFO:     Application startup complete.', 'INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)']
health status as Docker sees it (from the HEALTHCHECK in the Dockerfile): healthy
$ docker rm -f pbtut-churn
  pbtut-churn
cleaned up: my container and my image removed; yours untouched -> ['crm_db', 'crm_adminer', 'crm_app', 'crm_webserver']
```

The container's answer is **bit-identical** to the local one, which is the whole point of pinning the environment. (Notice the image size, about 850 MB: the slim Python base is 181 MB and scikit-learn, SciPy, pandas and NumPy make up most of the rest. A serving image should install only what the model needs; ml.07 shows how exporting the model to ONNX shrinks it.) Change `scikit-learn==...` in `requirements.txt` to another version, rebuild, and watch what happens: either the pickle refuses to load, or you get a warning about "unpickling from version X when using version Y". That is the *training-serving environment* mismatch, the quietest cousin of the problem the next section is about.

**Question.** A teammate says: "Docker already isolates everything, so we don't need to pin versions in `requirements.txt`; `pip install scikit-learn` always gets the latest." What goes wrong?

<details><summary>Answer</summary>

The image is only reproducible if its *contents* are. `pip install scikit-learn` resolves to whatever is newest on the day you build, so a rebuild next month can produce a different environment than the one the model was trained and validated in: a different scikit-learn can load the pickle with a warning, change numeric behaviour, or fail. Pin exact versions (a lockfile, or a `requirements.txt` generated from the training environment), keep the pins in git with the code, and record them with the run (MLflow stored `requirements.txt` next to the model for this reason). Docker removes differences between *machines*; pinning removes differences between *builds*.

</details>

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw a Docker image for the churn service as stacked layers: base python:3.14-slim, pip install of pinned requirements (fastapi, scikit-learn, numpy, pandas), the service code, the model folder (model.joblib, meta.json). Show 'docker build' creating the image, 'docker run -p 127.0.0.1:18081:8000' starting a container from it, and a client on the host calling localhost:18081/predict. Mark the layer order that makes rebuilds fast (dependencies before code) and show a non-root user and a HEALTHCHECK."

### 5.4 Try it

1. Add a `GET /ready` endpoint that returns 503 until the model is loaded. Why do orchestrators distinguish *liveness* ("the process is up") from *readiness* ("it can serve")?
2. Make the log writer robust: what happens to `predictions.jsonl` when two uvicorn workers run the app? (Two processes, two locks.) Suggest a fix that does not need locks.
3. Add the field `plan: Literal[...]` a fourth value `"enterprise"` to the contract only. What happens to requests that use it, and where else must the change be made for them to be scored correctly?

## 6. Training-serving consistency

### 6.1 The bug that unit tests do not catch

**Training-serving skew** is a difference between how features are computed when the model is *trained* and when it *serves*. The model is not wrong; it is being fed something other than what it learned from. It does not crash. It produces plausible numbers that are quietly worse. Typical causes:

| Cause | Example |
|---|---|
| **Two code paths** | training uses a pandas pipeline; serving re-implements it by hand and drifts |
| **Units and scales** | the app sends spend in cents, training had euros |
| **Category handling** | different category order in a hand-written one-hot; a new category unseen in training |
| **Missing values** | training imputes the median; serving fills 0 |
| **Time** | a feature computed with information from the *future* of the prediction time (leakage) |
| **Stale data** | a feature table refreshed daily at training, hourly at serving |

### 6.2 Skew made visible

The service above is safe because **preprocessing lives inside the pipeline artifact**: the same fitted object trains and serves. The more common real-world path is the opposite: someone "reimplements the preprocessing in the API for speed". Here is that path, with three realistic mistakes, compared with the truth:

```python run
trained_pipe = champion                                           # the real artefact: scaler + one-hot + model in one object
sc, cats = trained_pipe.named_steps["prep"].named_transformers_["num"], trained_pipe.named_steps["prep"].named_transformers_["cat"]
lr = trained_pipe.named_steps["model"]
print("one-hot column order the model was trained with:", list(cats.get_feature_names_out()))

def reimplemented(frame, spend_in_cents=False, wrong_order=False, fill_missing_with_zero=False):
    """The 'hand-written serving preprocessing', with the classic mistakes switched on one at a time."""
    f = frame.copy()
    if spend_in_cents: f["monthly_spend"] = f["monthly_spend"] * 100                           # the app sends cents
    X_num = (f[NUM].to_numpy(float) - sc.mean_) / sc.scale_                                    # same scaling formula, same fitted numbers
    plan_order = ["premium", "basic", "standard"] if wrong_order else list(cats.categories_[0])  # someone sorted differently
    X_plan = np.stack([(f["plan"] == p).to_numpy(float) for p in plan_order], 1)
    X_reg = np.stack([(f["region"] == r).to_numpy(float) for r in cats.categories_[1]], 1)
    return lr.predict_proba(np.hstack([X_num, X_plan, X_reg]))[:, 1]

X_h = holdout[NUM + CAT]
truth = trained_pipe.predict_proba(X_h)[:, 1]
rows = []
for label, kw in [("faithful re-implementation", {}), ("spend sent in cents", dict(spend_in_cents=True)), ("plan columns in a different order", dict(wrong_order=True))]:
    p = reimplemented(X_h, **kw)
    rows.append([label, f"{np.abs(p - truth).max():.2e}", f"{np.mean((p >= 0.5) != (truth >= 0.5)):.1%}", round(roc_auc_score(y_h, p), 4)])
print(pd.DataFrame(rows, columns=["serving code", "max |score difference|", "decisions that flip", "AUC on holdout"]).to_string(index=False))
print(f"(the real pipeline's holdout AUC is {roc_auc_score(y_h, truth):.4f})")
```
```text
one-hot column order the model was trained with: ['plan_basic', 'plan_premium', 'plan_standard', 'region_east', 'region_north', 'region_south', 'region_west']
                     serving code max |score difference| decisions that flip  AUC on holdout
       faithful re-implementation               0.00e+00                0.0%          0.6818
              spend sent in cents               9.81e-01               91.5%          0.5096
plan columns in a different order               1.77e-01                5.7%          0.6416
(the real pipeline's holdout AUC is 0.6818)
```

Read the table: the faithful copy matches to rounding error, so a re-implementation *can* be right. The two bugs change scores and decisions, and the damage shows up as lower AUC, **with no exception anywhere**. The "plan columns in a different order" bug is the nasty one: the numbers are all valid, only the meaning of each column is wrong.

### 6.3 Four defences

1. **One artifact, one code path.** Put every transformation inside the saved pipeline (`ColumnTransformer`, `FunctionTransformer`), or put shared feature code in a library imported by both training and serving. This is what `Pipeline` is for (ds.05).
2. **A contract at the door.** The pydantic `Customer` model rejects wrong types, impossible ranges and unknown categories. It cannot catch "plausible but wrong units" (4500 cents is a valid number), which is why the next section monitors input distributions.
3. **A parity test.** Keep a small *golden set* of inputs and the scores the offline pipeline gives. The test calls the **service** and compares. It would have caught every row of the table above.
4. **Log what you served.** Store the exact feature vector the model received, so any suspicious prediction can be replayed offline.

```python run
def assert_parity(client, frame, offline_scores, atol=1e-5):
    """Call the SERVICE on the golden rows and compare with the offline pipeline."""
    got = np.array(client.post("/predict/batch", json={"customers": frame.to_dict("records")}).json()["churn_probability"])
    worst = float(np.abs(got - offline_scores).max())
    assert worst <= atol, f"serving differs from training: max |diff| = {worst:.2e} (check units, category order, missing-value handling)"
    return worst

golden = X_h.head(300)
print("parity test on the real service: max |diff| =", assert_parity(api, golden, truth[:300]), "-> passes")
try: assert_parity(api, golden.assign(monthly_spend=golden.monthly_spend * 1.5), truth[:300])          # simulate a units bug upstream
except AssertionError as e: print("with a units bug upstream the test fails:", e)
```
```text
parity test on the real service: max |diff| = 4.998581695225823e-07 -> passes
with a units bug upstream the test fails: serving differs from training: max |diff| = 6.79e-02 (check units, category order, missing-value handling)
```

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw two pictures of training and serving. Picture 1 (skew): training reads a table, runs preprocessing code A, and fits a model; serving receives a JSON request, runs a separately written preprocessing code B, and calls the model; mark the places where A and B can differ (units, category order, missing values) in red. Picture 2 (fixed): one saved Pipeline object containing preprocessing and model is used on both sides, and a parity test feeds 300 golden rows through both and compares scores."

### 6.4 Time: the leakage you only see in production

The subtlest skew is about **time**. A feature must be computed from information that existed *at prediction time*. Build a tiny event log to see it: each customer has a prediction date `t0`, support tickets scattered over time, and churn *after* `t0`. A careless "total tickets" feature, computed over the whole log, includes tickets that happened **after** `t0`. (Customers who are about to leave call support to cancel.) Offline it looks wonderful. In production those tickets do not exist yet.

```python run
rng = np.random.default_rng(3)
n = 4000
latent = rng.normal(size=n)                                                       # hidden 'will churn' tendency
churn = (rng.random(n) < 1 / (1 + np.exp(-(latent * 0.8 - 0.8)))).astype(int)
before = rng.poisson(np.exp(0.2 + 0.25 * latent))                                 # tickets in the 30 days BEFORE t0: weak real signal
after = np.where(churn == 1, rng.poisson(3.0, n), rng.poisson(0.3, n))            # tickets AFTER t0: churners call to cancel -> strong, but from the future
ev = pd.DataFrame({"churn": churn, "tickets_before_t0": before, "tickets_after_t0": after})
ev["tickets_total_naive"] = ev.tickets_before_t0 + ev.tickets_after_t0            # "total tickets in the log" (what a careless query returns)
tr_i, te_i = train_test_split(np.arange(n), test_size=0.3, random_state=0, stratify=churn)
for feature in ("tickets_total_naive", "tickets_before_t0"):
    m = LogisticRegression().fit(ev.loc[tr_i, [feature]], ev.loc[tr_i, "churn"])
    print(f"{feature:<22} offline AUC {roc_auc_score(ev.loc[te_i, 'churn'], m.predict_proba(ev.loc[te_i, [feature]])[:, 1]):.3f}")
print("\nIn production only tickets BEFORE t0 exist; the naive model is fed tickets_total = tickets_before only.")
m = LogisticRegression().fit(ev.loc[tr_i, ["tickets_total_naive"]], ev.loc[tr_i, "churn"])
served = ev.loc[te_i, ["tickets_before_t0"]].rename(columns={"tickets_before_t0": "tickets_total_naive"})
print(f"naive model's AUC when served honestly: {roc_auc_score(ev.loc[te_i, 'churn'], m.predict_proba(served)[:, 1]):.3f}")
```
```text
tickets_total_naive    offline AUC 0.882
tickets_before_t0      offline AUC 0.516

In production only tickets BEFORE t0 exist; the naive model is fed tickets_total = tickets_before only.
naive model's AUC when served honestly: 0.516
```

The naive feature gives an impressive offline AUC and collapses when served with what is really available. The fix is **point-in-time correct features**: every feature is computed "as of" `t0`. In pandas that is a filter on event time or `pd.merge_asof`; in a feature store it is built in. The test is easy to state: *for each training row, can I name the moment the prediction would have been made, and does every feature use only data before that moment?*

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw a timeline for one customer with a vertical line at t0 labelled 'prediction time'. Put small tick marks for support tickets on both sides. Shade the region before t0 green and label it 'allowed for features', shade the region after t0 red and label it 'future: leakage'. Show 'tickets_total_naive' as a bracket covering both sides and 'tickets_before_t0' as a bracket covering only the green side. Add a churn event marker after t0."

### 6.5 Try it

1. Add a `plan` value that never appeared in training (`"enterprise"`) to `reimplemented` and to the real pipeline. Which one handles it gracefully (`handle_unknown="ignore"`), and what does the model effectively assume about such a customer?
2. In `reimplemented`, fill missing `monthly_spend` with 0 while training used the median. Construct a holdout where 5% of spend is missing and measure the AUC loss.
3. Write the parity test as a `pytest` test that is run in CI before every deploy. What should it do when the golden file legitimately changes (a new model version)?

## 7. Monitoring and drift

### 7.1 A model decays without any code change

A deployed model is a bet that tomorrow's inputs look like yesterday's training data. The bet loses when customers change (a price rise, a new region, a marketing campaign), when an upstream system changes a field's meaning, or when the world changes the relationship between inputs and outcome. You monitor three layers:

| Layer | What to watch | Needs labels? | Reacts in |
|---|---|---|---|
| **Service** | request rate, error rate, latency percentiles, availability | no | seconds |
| **Data** | each input's distribution, missing-value rate, new categories, schema | no | hours |
| **Model** | the score distribution; and, when outcomes arrive, accuracy/AUC | only the last one | days to months |

The syllabus outcome, *detect drift in a served model*, lives in the middle row. Three kinds of drift matter, because they need different detectors:

| Drift | What changes | Visible without labels? |
|---|---|---|
| **Covariate (data) drift** | the distribution of inputs `P(x)` | yes |
| **Label (prior) drift** | how often the outcome happens `P(y)` | only through scores or labels |
| **Concept drift** | the relationship `P(y given x)` | **no**: inputs can look unchanged |

**Service metrics first.** The service from section 5 counts requests and records a latency histogram; `/metrics` prints them in the text format that Prometheus scrapes. This is the output after the traffic we sent in section 5:

```python run
r = api.get("/metrics"); print(r.text.strip())
print("\nreading it: a Prometheus alert would compare, for example, the share of requests slower than 50 ms:")
lines = {l.split()[0]: float(l.split()[1]) for l in r.text.splitlines() if l and not l.startswith("#")}
slow = 1 - lines['churn_request_latency_ms_bucket{le="50"}'] / lines['churn_request_latency_ms_count']
print(f"  requests so far {int(lines['churn_requests_total'])}, customers scored {int(lines['churn_predictions_total'])}, "
      f"slower than 50 ms: {slow:.1%}")
```
```text
# TYPE churn_requests_total counter
churn_requests_total 208
# TYPE churn_predictions_total counter
churn_predictions_total 1007
# TYPE churn_request_latency_ms histogram
churn_request_latency_ms_bucket{le="5"} 31
churn_request_latency_ms_bucket{le="10"} 196
churn_request_latency_ms_bucket{le="25"} 207
churn_request_latency_ms_bucket{le="50"} 207
churn_request_latency_ms_bucket{le="100"} 207
churn_request_latency_ms_bucket{le="250"} 208
churn_request_latency_ms_bucket{le="1000"} 208
churn_request_latency_ms_bucket{le="+Inf"} 208
churn_request_latency_ms_sum 1547.075
churn_request_latency_ms_count 208

reading it: a Prometheus alert would compare, for example, the share of requests slower than 50 ms:
  requests so far 208, customers scored 1007, slower than 50 ms: 0.5%
```

### 7.2 Drift statistics, written from scratch

For a numeric feature you compare the **reference** sample (the training data) with a **current** window of production data. Two standard tools:

- **PSI** (population stability index): cut the reference into bins (deciles), count the share of each sample in each bin, and add up `(cur − ref) · ln(cur / ref)`. It is a distance, `0` means identical; common rules of thumb: below 0.1 stable, 0.1 to 0.25 moderate shift, above 0.25 major shift.
- **Kolmogorov-Smirnov test** (`scipy.stats.ks_2samp`): the largest gap between the two cumulative distributions, with a p-value.

For a categorical feature compare category shares (PSI on the categories, or a chi-square test).

```python run
from scipy import stats

def psi_numeric(ref, cur, bins=10, eps=1e-4):
    edges = np.unique(np.quantile(ref, np.linspace(0, 1, bins + 1)))
    edges[0], edges[-1] = -np.inf, np.inf
    p = np.histogram(ref, edges)[0] / len(ref); q = np.histogram(cur, edges)[0] / len(cur)
    p, q = np.clip(p, eps, None), np.clip(q, eps, None)
    return float(np.sum((q - p) * np.log(q / p)))

def psi_categorical(ref, cur, eps=1e-4):
    cats = sorted(set(ref) | set(cur))
    p = np.array([np.mean(np.asarray(ref) == c) for c in cats]).clip(eps); q = np.array([np.mean(np.asarray(cur) == c) for c in cats]).clip(eps)
    return float(np.sum((q - p) * np.log(q / p)))

ref = make_customers(8000, seed=0)                                   # reference: training-time data
same = make_customers(1000, seed=11)                                 # new window, same world
shifted = make_customers(1000, seed=12, spend_shift=1.25)            # spend is 25% higher
print(f"{'window':<22}{'PSI(monthly_spend)':>20}{'KS statistic':>15}{'KS p-value':>13}")
for name, win in (("same distribution", same), ("spend +25%", shifted)):
    ks = stats.ks_2samp(ref.monthly_spend, win.monthly_spend)
    print(f"{name:<22}{psi_numeric(ref.monthly_spend, win.monthly_spend):>20.4f}{ks.statistic:>15.4f}{ks.pvalue:>13.2g}")
print("categorical 'plan' PSI, same window:", round(psi_categorical(ref.plan, same.plan), 4), "| window with more premium customers:",
      round(psi_categorical(ref.plan, make_customers(1000, seed=13, premium_boost=0.12).plan), 4))
```
```text
window                  PSI(monthly_spend)   KS statistic   KS p-value
same distribution                   0.0149         0.0346         0.23
spend +25%                          0.2299         0.1633      3.8e-21
categorical 'plan' PSI, same window: 0.0016 | window with more premium customers: 0.0925
```

**Statistical significance is not practical significance.** A test p-value answers "is there *any* difference?", and with enough rows there always is. PSI measures *how large*. The same small 5% shift in spend, windows of growing size:

```python run
rows = []
for n in (200, 1000, 10000, 100000):
    win = make_customers(n, seed=50, spend_shift=1.05)
    rows.append([n, round(psi_numeric(ref.monthly_spend, win.monthly_spend), 4), f"{stats.ks_2samp(ref.monthly_spend, win.monthly_spend).pvalue:.2g}"])
print(pd.DataFrame(rows, columns=["rows in window", "PSI", "KS p-value"]).to_string(index=False))
```
```text
 rows in window    PSI KS p-value
            200 0.0398       0.45
           1000 0.0120       0.03
          10000 0.0106    2.9e-05
         100000 0.0094    9.9e-09
```

The p-value falls to almost nothing as the window grows although the shift is always the same 5%, so a rule "alert when p < 0.05" would page you every night on a busy service. The PSI stays small. Alert on *size* of change; use the test for a second opinion on small windows.

**Calibrate your threshold with no-drift windows.** The 0.1/0.25 rules came from credit scoring; your PSI on 200-row windows is noisier than on 10,000-row windows. Measure it by sampling many windows from the *reference world* (no drift) and looking at the spread:

```python run
rng = np.random.default_rng(0)
ref_spend = ref.monthly_spend.to_numpy()
rows = []
for n in (100, 300, 1000, 5000):
    vals = [psi_numeric(ref_spend, rng.choice(ref_spend, n)) for _ in range(300)]
    rows.append([n, round(np.mean(vals), 4), round(np.percentile(vals, 99), 4)])
print(pd.DataFrame(rows, columns=["window size", "mean PSI, NO drift", "99th percentile, NO drift"]).to_string(index=False))
```
```text
 window size  mean PSI, NO drift  99th percentile, NO drift
         100              0.0923                     0.2304
         300              0.0308                     0.0822
        1000              0.0092                     0.0235
        5000              0.0018                     0.0043
```

On 100-row windows even a stable feature reaches a PSI near 0.1 by chance, so a threshold of 0.1 would raise false alarms constantly; at 5,000 rows it is tiny. **A drift alert needs a minimum window size and a threshold tied to it.**

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw how PSI is computed for monthly_spend. Show the reference histogram cut into 10 decile bins (each holding 10% of the reference) next to a current-window histogram of the same bins where the high-spend bins hold more customers (spend +25%). Under the bars write the per-bin term (cur minus ref) times ln(cur over ref), highlight the biggest terms, and sum them to a PSI value. Add a gauge with zones: below 0.1 stable, 0.1 to 0.25 moderate, above 0.25 major."

### 7.3 A 30-day deployment, with drift injected on day 15

We know the truth, so we can check the monitor against it. Thirty days of traffic, 500 customers a day, scored by the champion. **Days 1 to 14: the training world. From day 15: a price change** makes spend 25% higher and brings 10% more premium customers (covariate drift). The monitor sees only inputs and scores, never labels.

```python run
ref_train = make_customers(4500, seed=0)                                          # the reference the model was trained on (same recipe as section 2)
ref_scores = champion.predict_proba(ref_train[NUM + CAT])[:, 1]
def day_traffic(day, **kw): return make_customers(500, seed=1000 + day, **kw)
daily = {d: day_traffic(d, **({"spend_shift": 1.25, "premium_boost": 0.10} if d >= 15 else {})) for d in range(1, 31)}

def drift_report(window, ref=ref_train, ref_scores=ref_scores, min_rows=300, psi_alert=0.2):
    if len(window) < min_rows: return {"status": "insufficient data", "n": len(window)}
    rep = {"n": len(window), "psi": {c: psi_numeric(ref[c], window[c]) for c in NUM}}
    rep["psi"].update({c: psi_categorical(ref[c], window[c]) for c in CAT})
    rep["score_psi"] = psi_numeric(ref_scores, champion.predict_proba(window[NUM + CAT])[:, 1])
    rep["alerts"] = sorted([c for c, v in rep["psi"].items() if v > psi_alert])
    rep["status"] = "DRIFT" if rep["alerts"] else "ok"
    return rep

reports = {d: drift_report(daily[d]) for d in range(1, 31)}
tbl = pd.DataFrame([{"day": d, "status": r["status"], "psi_spend": round(r["psi"]["monthly_spend"], 3), "psi_plan": round(r["psi"]["plan"], 3), "psi_tickets": round(r["psi"]["support_tickets"], 3),
                     "psi_score": round(r["score_psi"], 3), "alerts": ",".join(r["alerts"])} for d, r in reports.items() if d in (1, 7, 13, 14, 15, 16, 17, 22, 30)])
print(tbl.to_string(index=False))
status = [reports[d]["status"] for d in range(1, 31)]
first = next(d for d in range(2, 31) if status[d - 1] == status[d - 2] == "DRIFT")
print(f"\nfalse alarms on days 1-14: {sum(s == 'DRIFT' for s in status[:14])} | days flagged after the change: {sum(s == 'DRIFT' for s in status[14:])} of 16")
print(f"rule 'two consecutive DRIFT days' fires on day {first} (drift was injected on day 15)")
```
```text
 day status  psi_spend  psi_plan  psi_tickets  psi_score        alerts
   1     ok      0.028     0.004        0.001      0.029              
   7     ok      0.015     0.013        0.007      0.015              
  13     ok      0.032     0.007        0.001      0.024              
  14     ok      0.009     0.001        0.002      0.011              
  15  DRIFT      0.434     0.109        0.006      0.035 monthly_spend
  16  DRIFT      0.463     0.082        0.015      0.012 monthly_spend
  17  DRIFT      0.445     0.087        0.008      0.017 monthly_spend
  22  DRIFT      0.410     0.075        0.001      0.013 monthly_spend
  30  DRIFT      0.415     0.070        0.006      0.021 monthly_spend

false alarms on days 1-14: 0 | days flagged after the change: 16 of 16
rule 'two consecutive DRIFT days' fires on day 16 (drift was injected on day 15)
```

Read what the table says. The per-feature PSI points at the cause (`monthly_spend` and `plan`), **not** `support_tickets` (which did not change), and the *score* PSI shows how much the model's output moved as a result (very little here, 0.01 to 0.04, because this model barely uses spend; keep that in mind for 7.4). That is a monitor doing its job: it does not only say "something changed", it says *where*.

### 7.4 Drift is not damage: the case for watching outcomes too

Does the model get worse after the price change? Churn labels arrive late (a customer who will leave in week 3 is not known to churn until then), but because our data are generated we can look ahead and compare. Then a **second** scenario: *concept drift*, where the inputs look exactly like training but the relationship changes (support tickets stop predicting churn):

```python run
scenarios = {"no change": {}, "covariate drift (spend +25%, more premium)": {"spend_shift": 1.25, "premium_boost": 0.10}, "concept drift (tickets no longer predict churn)": {"concept": 0.5}}
rows = []
for name, kw in scenarios.items():
    win = make_customers(6000, seed=77, **kw)
    s = champion.predict_proba(win[NUM + CAT])[:, 1]
    rep = drift_report(win)
    rows.append([name, round(max(rep["psi"].values()), 3), round(rep["score_psi"], 3), rep["status"], round(roc_auc_score(win[TARGET], s), 3)])
print(pd.DataFrame(rows, columns=["scenario (6,000 customers)", "worst feature PSI", "score PSI", "input monitor says", "AUC once labels arrive"]).to_string(index=False))
```
```text
                     scenario (6,000 customers)  worst feature PSI  score PSI input monitor says  AUC once labels arrive
                                      no change              0.003      0.004                 ok                   0.687
     covariate drift (spend +25%, more premium)              0.369      0.004              DRIFT                   0.690
concept drift (tickets no longer predict churn)              0.003      0.004                 ok                   0.592
```

Two lessons in one table. **Covariate drift raises the alarm but need not hurt**: the monitor fires, yet the AUC is about as before, because spend is only weakly related to churn here. An alert means *risk*, not proof, so the response to an alert is to investigate, not to retrain blindly. **Concept drift is invisible to the input monitor**: PSI says "ok" while the AUC falls, because nothing about the inputs changed. Only outcomes expose it, which is why a mature setup also tracks **performance as labels arrive** (weekly AUC on the customers whose outcome is now known) and keeps a **delayed-label dashboard**.

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw a 2 by 2 grid with 'inputs look different?' (no, yes) on one axis and 'model gets worse?' (no, yes) on the other. Top-left: stable world. Top-right: covariate drift, alarm fires, no damage (false alarm for harm, still worth a look). Bottom-left: concept drift, input monitor silent, model getting worse (the dangerous cell, only outcome monitoring catches it). Bottom-right: both. For each cell give the example from a churn model (price rise; tickets stop predicting churn) and the monitor that catches it."

**Question.** Your drift monitor fires on day 15. Name the first three things to do, in order.

<details><summary>Answer</summary>

1. **Check for a data bug before assuming a real change**: did an upstream system change units, a default value, a field name, or stop sending a field? (A sudden, sharp shift in a single feature is more often a pipeline bug than the customers changing.) 2. **Find out which features and which segment moved** (the per-feature PSI above), and whether the score distribution moved. 3. **Estimate the harm**: replay recent data through the model with whatever labels exist, or compare with a shadow model, before deciding. Retraining on shifted data, validated through the gate of section 4 on a holdout that reflects *today's* world, is the *consequence* of that investigation, not the first reflex.

</details>

### 7.5 A monitoring checklist

1. Log every prediction with its inputs, score and model version (section 5).
2. Compute daily per-feature PSI against the training reference, with a minimum window size and a threshold calibrated on no-drift windows.
3. Track the score distribution, the missing-value rate per feature, and the share of unseen categories.
4. Track latency, error rate and traffic; page on symptoms users feel.
5. Join outcomes as they arrive; chart performance by cohort week.
6. Write the runbook (who is paged, what to check first, how to roll back) *before* the first alert.

## 8. CI for ML and safe releases

### 8.1 What to test, beyond code

Ordinary unit tests check code. An ML pipeline also needs tests on **data** and on the **trained model**, because it can fail while all code is correct:

| Test layer | Example | Runs |
|---|---|---|
| **Code** | the feature function returns the right frame | every commit |
| **Data** | schema, ranges, null rate, duplicate ids, class balance, no target leakage | every data update |
| **Pipeline smoke** | train on 300 rows end to end, finish in seconds | every commit |
| **Model** | seeded determinism; AUC above a floor on a fixed holdout; no big drop on any key slice | every candidate |
| **Service** | contract (422 on bad input), parity with the offline pipeline | every build |
| **Gate** | candidate vs champion with an interval (section 4) | before promotion |

Data tests are the cheapest and catch the most. A small checker, then a clean dataset and four ways to break it:

```python run
def data_checks(d, ref=ref_train, max_null=0.02, leak_corr=0.95):
    problems = []
    missing_cols = set(NUM + CAT + [TARGET, "customer_id"]) - set(d.columns)
    if missing_cols: return [f"schema: missing columns {sorted(missing_cols)}"]
    if d.customer_id.duplicated().any(): problems.append(f"duplicate customer ids: {int(d.customer_id.duplicated().sum())}")
    for c in NUM + CAT:
        nulls = d[c].isna().mean()
        if nulls > max_null: problems.append(f"null rate of {c} is {nulls:.0%} (limit {max_null:.0%})")
    for c, (lo, hi) in {"tenure_months": (0, 600), "monthly_spend": (0, 10000), "support_tickets": (0, 500)}.items():
        if d[c].min() < lo or d[c].max() > hi: problems.append(f"{c} outside [{lo}, {hi}]: min {d[c].min():.2f}, max {d[c].max():.2f}")
    if not set(d.plan.dropna()) <= set(PLANS): problems.append(f"unknown plans: {sorted(set(d.plan.dropna()) - set(PLANS))}")
    if not 0.05 < d[TARGET].mean() < 0.60: problems.append(f"churn rate {d[TARGET].mean():.1%} looks wrong")
    for c in NUM:
        if abs(d[c].corr(d[TARGET])) > leak_corr: problems.append(f"{c} is almost the target (corr {d[c].corr(d[TARGET]):.2f}): leakage?")
    return problems

clean = make_customers(3000, seed=4)
broken = {"clean data": clean,
          "20% of spend missing": clean.assign(monthly_spend=clean.monthly_spend.mask(np.random.default_rng(0).random(len(clean)) < 0.2)),
          "a plan 'gold' appears": clean.assign(plan=clean.plan.where(clean.index % 50 != 0, "gold")),
          "ids duplicated by a bad join": pd.concat([clean, clean.head(300)]),
          "future info in a feature": clean.assign(support_tickets=clean[TARGET] * 10 + np.random.default_rng(1).normal(0, 0.1, len(clean))),
          "a column renamed upstream": clean.rename(columns={"region": "area"})}
for name, d in broken.items():
    print(f"{name:<30} -> {data_checks(d) or 'ok'}")
```
```text
clean data                     -> ok
20% of spend missing           -> ['null rate of monthly_spend is 21% (limit 2%)']
a plan 'gold' appears          -> ["unknown plans: ['gold']"]
ids duplicated by a bad join   -> ['duplicate customer ids: 300']
future info in a feature       -> ['support_tickets outside [0, 500]: min -0.35, max 10.32', 'support_tickets is almost the target (corr 1.00): leakage?']
a column renamed upstream      -> ["schema: missing columns ['region']"]
```

### 8.2 The pipeline in CI

The workflow file is the same shape as swe.09's. *Shown, not run here (it needs a GitHub repository):*

```yaml
name: ml-ci
on: [pull_request]
jobs:
  checks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: {python-version: "3.14", cache: pip}
      - run: pip install -r requirements.txt pytest dvc
      - run: pytest -q tests/                    # code, data, smoke, service-contract and parity tests
      - run: dvc pull data/customers.csv && python -m churn_ops.check_data data/customers.csv
      - run: dvc repro --dry                     # fails if dvc.lock is out of date with params.yaml / code
      - run: docker build -t churn:${{ github.sha }} .
  gate:                                          # only on PRs that change model code or params
    needs: checks
    steps:
      - run: python -m churn_ops.gate --candidate runs:/${RUN_ID}/model --champion models:/churn-model@champion --holdout data/holdout.csv
```

Two ideas worth remembering: CI should run **fast** tests on every commit (a 300-row smoke training, not the full retrain), and the expensive training and the **gate** should be separate, triggered jobs. A failing gate must block the merge exactly like a failing unit test.

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw a CI pipeline for an ML repository as a horizontal flow: commit, fast tests (code tests, data tests, 300-row training smoke test), build Docker image, then a separate slower branch 'train candidate, register, run gate against champion with a confidence interval'. Show green and red outcomes: a data test failing on 20% null spend stops the flow early; a gate with interval lower bound below zero blocks the merge. Label which steps run on every commit and which only when model code or params change."

### 8.3 Try it

1. Add a data check for **drift against the reference** (PSI above 0.25 on any feature fails the check). When would you want this to *warn* instead of fail?
2. Write a model test that asserts predictions are **monotone** in `support_tickets` (more tickets never lowers the churn probability, other inputs fixed). Which models can fail such a test, and why might you want it for a credit or medical model?
3. Add a pytest that trains twice with the same seed and asserts identical metrics. What does it catch that code review does not?

## 9. Project: deploy and monitor a model as a service

### 9.1 The brief

Build the loop of this chapter as one small, tested package, **`churn_ops`**, and run it end to end:

1. **Track**: train through a function that logs params, metrics, the data hash and the model folder to MLflow, and can **reproduce** a run from its record.
2. **Serve**: the FastAPI service of section 5 serves the exported model folder and logs every prediction.
3. **Monitor**: a `Reference` fitted on the training data and a `drift_report` over windows read from the prediction log, with a minimum window size.
4. **Gate**: `should_promote` compares a candidate with the champion on a holdout with a confidence interval.
5. **Release**: promote the candidate by switching the model folder the service loads (in production, by moving the registry alias of section 4), restart the service, and keep the old folder as a rollback.
6. **Tests** for the properties that matter, runnable offline in seconds.

### 9.2 The module

```python run
proj = ws / "churn_ops_project"; (proj / "tests").mkdir(parents=True)
(proj / "churn_ops.py").write_text('''"""churn_ops: tracked training, export, drift monitoring and a promotion gate for the churn model."""
import hashlib, json, time
from pathlib import Path

import joblib
import mlflow
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

PLANS, REGIONS = ["basic", "standard", "premium"], ["north", "south", "east", "west"]
NUM, CAT, TARGET = ["tenure_months", "monthly_spend", "support_tickets"], ["plan", "region"], "churned"


def make_customers(n, seed=0, spend_shift=1.0, premium_boost=0.0, concept=0.0):
    rng = np.random.default_rng(seed)
    plan = rng.choice(PLANS, n, p=[0.50 - premium_boost, 0.35, 0.15 + premium_boost])
    base = pd.Series(plan).map({"basic": 25.0, "standard": 45.0, "premium": 80.0}).to_numpy()
    spend = (base * rng.lognormal(0.0, 0.30, n) * spend_shift).round(2)
    tenure = rng.gamma(2.0, 12.0, n).round(1)
    tickets = rng.poisson(1.2, n)
    region = rng.choice(REGIONS, n)
    z = -0.7 - 0.035 * tenure + (0.45 - 0.9 * concept) * tickets + 0.008 * (spend - base * spend_shift) + (plan == "premium") * -0.5
    churned = (rng.random(n) < 1 / (1 + np.exp(-z))).astype(int)
    return pd.DataFrame({"customer_id": np.arange(n), "tenure_months": tenure, "monthly_spend": spend, "support_tickets": tickets,
                         "plan": plan, "region": region, TARGET: churned})


def file_sha256(path, n=16):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()[:n]


def build_pipeline(params):
    prep = ColumnTransformer([("num", StandardScaler(), NUM), ("cat", OneHotEncoder(handle_unknown="ignore"), CAT)])
    return Pipeline([("prep", prep), ("model", LogisticRegression(C=params["C"], max_iter=1000))])


# ---------- tracked training ----------
def train_and_track(params, data_path, model_dir, tracking_uri, experiment="churn"):
    """Train, log to MLflow (params, metrics, data hash), export a serving folder. Returns a small record."""
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(experiment)
    df = pd.read_csv(data_path)
    tr, te = train_test_split(df, test_size=params["test_size"], random_state=params["seed"], stratify=df[TARGET])
    pipe = build_pipeline(params).fit(tr[NUM + CAT], tr[TARGET])
    auc = float(roc_auc_score(te[TARGET], pipe.predict_proba(te[NUM + CAT])[:, 1]))
    with mlflow.start_run() as run:
        mlflow.log_params(params)
        mlflow.set_tag("data_sha256", file_sha256(data_path))
        mlflow.log_metric("auc", auc)
        version = f"run-{run.info.run_id[:8]}"
        model_dir = Path(model_dir); model_dir.mkdir(parents=True, exist_ok=True)
        joblib.dump(pipe, model_dir / "model.joblib")
        meta = {"model_name": "churn-model", "model_version": version, "mlflow_run_id": run.info.run_id, "data_sha256": file_sha256(data_path),
                "features": NUM + CAT, "decision_threshold": 0.5, "trained_rows": int(len(tr)), "auc": round(auc, 5)}
        (model_dir / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
        mlflow.log_artifact(str(model_dir / "meta.json"))
    return {"run_id": run.info.run_id, "auc": auc, "version": version}


def reproduce(run_id, data_path, tracking_uri):
    """Re-run a past experiment from its tracked config. Raises if the data changed. Returns (recorded_auc, new_auc)."""
    mlflow.set_tracking_uri(tracking_uri)
    run = mlflow.get_run(run_id)
    if run.data.tags["data_sha256"] != file_sha256(data_path):
        raise RuntimeError("data changed since this run: refusing to claim reproduction")
    p = run.data.params
    params = {"C": float(p["C"]), "seed": int(p["seed"]), "test_size": float(p["test_size"])}
    df = pd.read_csv(data_path)
    tr, te = train_test_split(df, test_size=params["test_size"], random_state=params["seed"], stratify=df[TARGET])
    pipe = build_pipeline(params).fit(tr[NUM + CAT], tr[TARGET])
    return run.data.metrics["auc"], float(roc_auc_score(te[TARGET], pipe.predict_proba(te[NUM + CAT])[:, 1]))


# ---------- drift monitoring ----------
def psi_numeric(ref, cur, edges, eps=1e-4):
    p = np.clip(np.histogram(ref, edges)[0] / len(ref), eps, None); q = np.clip(np.histogram(cur, edges)[0] / len(cur), eps, None)
    return float(np.sum((q - p) * np.log(q / p)))


def psi_categorical(ref_shares, cur_values, eps=1e-4):
    cats = sorted(set(ref_shares) | set(cur_values))
    p = np.array([ref_shares.get(c, 0.0) for c in cats]).clip(eps); q = np.array([np.mean(np.asarray(cur_values) == c) for c in cats]).clip(eps)
    return float(np.sum((q - p) * np.log(q / p)))


class Reference:
    """What 'normal' looked like at training time: decile edges for numbers, category shares, and the score distribution."""
    def __init__(self, df, scores, bins=10):
        self.edges = {}
        for c in NUM:
            e = np.unique(np.quantile(df[c], np.linspace(0, 1, bins + 1))); e[0], e[-1] = -np.inf, np.inf
            self.edges[c] = e
        self.values = {c: df[c].to_numpy() for c in NUM}
        self.shares = {c: df[c].value_counts(normalize=True).to_dict() for c in CAT}
        e = np.unique(np.quantile(scores, np.linspace(0, 1, bins + 1))); e[0], e[-1] = -np.inf, np.inf
        self.score_edges, self.scores = e, np.asarray(scores)


def drift_report(ref, window, scores, min_rows=300, psi_alert=0.2):
    if len(window) < min_rows:
        return {"status": "insufficient data", "n": len(window), "alerts": []}
    psi = {c: psi_numeric(ref.values[c], window[c].to_numpy(), ref.edges[c]) for c in NUM}
    psi.update({c: psi_categorical(ref.shares[c], window[c].tolist()) for c in CAT})
    alerts = sorted(c for c, v in psi.items() if v > psi_alert)
    return {"status": "DRIFT" if alerts else "ok", "n": len(window), "psi": psi, "alerts": alerts,
            "score_psi": psi_numeric(ref.scores, np.asarray(scores), ref.score_edges),
            "ks_p": {c: float(stats.ks_2samp(ref.values[c], window[c]).pvalue) for c in NUM}}


def read_prediction_log(path):
    rows = [json.loads(l) for l in Path(path).read_text(encoding="utf-8").splitlines() if l.strip()]
    return pd.DataFrame(rows)


def first_alert_day(statuses, consecutive=2):
    run = 0
    for day, s in enumerate(statuses, 1):
        run = run + 1 if s == "DRIFT" else 0
        if run >= consecutive:
            return day
    return None


# ---------- promotion gate ----------
def should_promote(y, p_champion, p_candidate, n_boot=400, seed=0, min_gain=0.0):
    rng = np.random.default_rng(seed); y = np.asarray(y); gains = []
    for _ in range(n_boot):
        i = rng.integers(0, len(y), len(y))
        if y[i].min() == y[i].max():
            continue
        gains.append(roc_auc_score(y[i], p_candidate[i]) - roc_auc_score(y[i], p_champion[i]))
    lo, hi = np.percentile(gains, [2.5, 97.5])
    return {"gain": float(np.mean(gains)), "interval": (float(lo), float(hi)), "promote": bool(lo > min_gain)}


def canary_bucket(customer_id, salt="canary-1"):
    return int(hashlib.sha256(f"{salt}:{customer_id}".encode()).hexdigest()[:8], 16) % 100
''', encoding="utf-8")
shutil.copy(svc / "churn_service.py", proj / "churn_service.py")
print("wrote churn_ops.py:", len((proj / "churn_ops.py").read_text(encoding="utf-8").splitlines()), "lines | churn_service.py copied from section 5")
```
```text
wrote churn_ops.py: 148 lines | churn_service.py copied from section 5
```

### 9.3 Run the whole loop

Step 1: **train and track** a first model; **reproduce** it from its record; step 2: **serve** it and replay 14 normal days plus 6 days after a price change.

```python run
sys.path.insert(0, str(proj))
import churn_ops as ops; importlib.reload(ops)
uri = f"sqlite:///{proj / 'mlflow.db'}"
mlflow.create_experiment("churn-project", artifact_location=(proj / "mlartifacts").as_uri()) if mlflow.get_experiment_by_name("churn-project") is None else None
train_csv = proj / "train.csv"; ops.make_customers(8000, seed=0).to_csv(train_csv, index=False)
params = {"C": 0.05, "seed": 0, "test_size": 0.25}
rec1 = ops.train_and_track(params, train_csv, proj / "model_v1", uri, experiment="churn-project")
print("step 1 | trained and tracked:", rec1["version"], "AUC", round(rec1["auc"], 5))
rec_auc, new_auc = ops.reproduce(rec1["run_id"], train_csv, uri)
print("       | reproduced from the MLflow record:", rec_auc == new_auc, f"({rec_auc:.6f} vs {new_auc:.6f})")

def load_service(model_dir, pred_log, name):
    """Import the service file under a fresh module name, pointed at a model folder (this is what a restart does)."""
    os.environ["MODEL_DIR"], os.environ["PRED_LOG"] = str(model_dir), str(pred_log)
    spec = importlib.util.spec_from_file_location(name, proj / "churn_service.py"); mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return TestClient(mod.app)

import importlib.util
log1 = proj / "predictions_v1.jsonl"
service = load_service(proj / "model_v1", log1, "churn_service_v1")
print("step 2 | service up:", service.get("/health").json())
daily_p = {d: ops.make_customers(500, seed=2000 + d, **({"spend_shift": 1.3, "premium_boost": 0.12} if d > 14 else {})).drop(columns=["customer_id", TARGET]) for d in range(1, 21)}
for d, frame in daily_p.items():
    service.post("/predict/batch", json={"customers": frame.to_dict("records")})
logged = ops.read_prediction_log(log1)
print("       | prediction log:", len(logged), "rows | columns:", list(logged.columns)[:6], "...")
```
```text
step 1 | trained and tracked: run-d83e7e11 AUC 0.67528
       | reproduced from the MLflow record: True (0.675281 vs 0.675281)
step 2 | service up: {'status': 'ok', 'model_version': 'run-d83e7e11'}
       | prediction log: 10000 rows | columns: ['ts', 'request_id', 'model_version', 'score', 'tenure_months', 'monthly_spend'] ...
```

Step 3: the **monitor** reads only the prediction log (what production actually saw), splits it into days of 500 rows, and compares each with the reference built from the training data.

```python run
train_df = pd.read_csv(train_csv)
pipe_v1 = joblib.load(proj / "model_v1" / "model.joblib")
reference = ops.Reference(train_df, pipe_v1.predict_proba(train_df[NUM + CAT])[:, 1])
days = [logged.iloc[i * 500:(i + 1) * 500] for i in range(20)]
reps = [ops.drift_report(reference, d[NUM + CAT], d["score"]) for d in days]
print(pd.DataFrame([{"day": i + 1, "status": r["status"], "psi_spend": round(r["psi"]["monthly_spend"], 3), "psi_plan": round(r["psi"]["plan"], 3), "score_psi": round(r["score_psi"], 3),
                     "alerts": ",".join(r["alerts"])} for i, r in enumerate(reps) if i + 1 in (1, 14, 15, 16, 20)]).to_string(index=False))
day = ops.first_alert_day([r["status"] for r in reps])
print(f"step 3 | alert rule (2 consecutive DRIFT days) fires on day {day}; the price change was injected on day 15")
print("       | a window of 120 rows is refused rather than guessed at:", ops.drift_report(reference, days[0].head(120)[NUM + CAT], days[0].head(120)["score"])["status"])
```
```text
 day status  psi_spend  psi_plan  score_psi        alerts
   1     ok      0.024     0.013      0.011              
  14     ok      0.009     0.011      0.027              
  15  DRIFT      0.522     0.117      0.011 monthly_spend
  16  DRIFT      0.480     0.090      0.022 monthly_spend
  20  DRIFT      0.636     0.171      0.064 monthly_spend
step 3 | alert rule (2 consecutive DRIFT days) fires on day 16; the price change was injected on day 15
       | a window of 120 rows is refused rather than guessed at: insufficient data
```

Step 4 and 5: **respond**. Retrain on data that reflects the new world, run the **gate on a holdout from the new world**, promote by moving the alias, restart the service on the new model, and keep the old folder as the rollback.

```python run
new_world = lambda n, seed: ops.make_customers(n, seed=seed, spend_shift=1.3, premium_boost=0.12)
train2_csv = proj / "train2.csv"; pd.concat([ops.make_customers(4000, seed=0), new_world(4000, 31)]).reset_index(drop=True).assign(customer_id=lambda d: range(len(d))).to_csv(train2_csv, index=False)
rec2 = ops.train_and_track(params, train2_csv, proj / "model_v2", uri, experiment="churn-project")
holdout_new = new_world(5000, 4242)
pipe_v2 = joblib.load(proj / "model_v2" / "model.joblib")
p_old, p_new = pipe_v1.predict_proba(holdout_new[NUM + CAT])[:, 1], pipe_v2.predict_proba(holdout_new[NUM + CAT])[:, 1]
g = ops.should_promote(holdout_new[TARGET].to_numpy(), p_old, p_new)
print(f"step 4 | gate on a holdout from the NEW world: AUC {roc_auc_score(holdout_new[TARGET], p_old):.4f} (old) vs {roc_auc_score(holdout_new[TARGET], p_new):.4f} (new) | gain {g['gain']:+.4f}, interval [{g['interval'][0]:+.4f}, {g['interval'][1]:+.4f}] -> promote: {g['promote']}")

log2 = proj / "predictions_v2.jsonl"
service2 = load_service(proj / "model_v2", log2, "churn_service_v2")                  # 'deploy': the service restarts on the promoted model folder
print("step 5 | service now serves:", service2.get("/health").json(), "| rollback folder kept:", (proj / "model_v1").name)
after = pd.concat([new_world(500, 5000 + i).drop(columns=["customer_id", TARGET]) for i in range(5)])
service2.post("/predict/batch", json={"customers": after.head(1000).to_dict("records")}); service2.post("/predict/batch", json={"customers": after.tail(1000).to_dict("records")})
l2 = ops.read_prediction_log(log2)
ref2 = ops.Reference(pd.read_csv(train2_csv), pipe_v2.predict_proba(pd.read_csv(train2_csv)[NUM + CAT])[:, 1])
r_new = ops.drift_report(ref2, l2[NUM + CAT].head(500), l2["score"].head(500))
r_old = ops.drift_report(reference, l2[NUM + CAT].head(500), l2["score"].head(500))
print(f"       | same live traffic seen by the OLD reference: {r_old['status']} (spend PSI {r_old['psi']['monthly_spend']:.3f}) | by the NEW reference: {r_new['status']} (spend PSI {r_new['psi']['monthly_spend']:.3f})")
```
```text
step 4 | gate on a holdout from the NEW world: AUC 0.6946 (old) vs 0.7015 (new) | gain +0.0068, interval [+0.0024, +0.0111] -> promote: True
step 5 | service now serves: {'status': 'ok', 'model_version': 'run-f2c58b60'} | rollback folder kept: model_v1
       | same live traffic seen by the OLD reference: DRIFT (spend PSI 0.592) | by the NEW reference: ok (spend PSI 0.169)
```

The loop is closed: drift detected from production logs only, a candidate trained for the new world, a gate with an interval on a holdout from that world, a switch of the served model with a rollback folder, and a monitor whose reference moves with the model.

### 9.4 Tests

```python run
(proj / "tests" / "test_churn_ops.py").write_text('''import json, sys
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import churn_ops as ops

PARAMS = {"C": 0.05, "seed": 0, "test_size": 0.25}


@pytest.fixture(scope="module")
def env(tmp_path_factory):
    d = tmp_path_factory.mktemp("ops")
    csv = d / "train.csv"; ops.make_customers(3000, seed=0).to_csv(csv, index=False)
    return d, csv, f"sqlite:///{d / 'mlflow.db'}"


def test_training_is_deterministic(env):
    d, csv, uri = env
    a = ops.train_and_track(PARAMS, csv, d / "m1", uri); b = ops.train_and_track(PARAMS, csv, d / "m2", uri)
    assert a["auc"] == b["auc"], "same data, same params, same seed must give identical metrics"


def test_reproduce_from_tracked_config(env):
    d, csv, uri = env
    rec = ops.train_and_track(PARAMS, csv, d / "m3", uri)
    recorded, rerun = ops.reproduce(rec["run_id"], csv, uri)
    assert recorded == rerun, "reproducing from the tracked config must give the recorded metric"


def test_reproduce_refuses_changed_data(env):
    d, csv, uri = env
    rec = ops.train_and_track(PARAMS, csv, d / "m4", uri)
    changed = d / "changed.csv"; pd.read_csv(csv).assign(monthly_spend=lambda x: x.monthly_spend * 1.01).to_csv(changed, index=False)
    with pytest.raises(RuntimeError, match="data changed"):
        ops.reproduce(rec["run_id"], changed, uri)


def test_export_folder_is_self_describing(env):
    d, csv, uri = env
    ops.train_and_track(PARAMS, csv, d / "m5", uri)
    meta = json.loads((d / "m5" / "meta.json").read_text(encoding="utf-8"))
    assert {"model_version", "data_sha256", "features", "decision_threshold"} <= set(meta), "the service needs these facts to identify and describe the model"


def _ref():
    df = ops.make_customers(5000, seed=0)
    return ops.Reference(df, np.random.default_rng(0).random(len(df)))


def test_no_false_alarm_on_the_same_world():
    ref = _ref(); alarms = 0
    for seed in range(40):
        w = ops.make_customers(500, seed=100 + seed)
        alarms += ops.drift_report(ref, w, np.random.default_rng(seed).random(500))["status"] == "DRIFT"
    assert alarms <= 1, f"{alarms} false alarms in 40 no-drift windows: the threshold is too tight for 500-row windows"


def test_alarm_on_injected_shift_and_it_names_the_cause():
    ref = _ref()
    rep = ops.drift_report(ref, ops.make_customers(500, seed=7, spend_shift=1.3, premium_boost=0.12), np.random.default_rng(1).random(500))
    assert rep["status"] == "DRIFT" and "monthly_spend" in rep["alerts"] and "support_tickets" not in rep["alerts"]


def test_tiny_window_is_refused():
    assert ops.drift_report(_ref(), ops.make_customers(50, seed=1), np.random.default_rng(1).random(50))["status"] == "insufficient data"


def test_alert_rule_needs_consecutive_days():
    assert ops.first_alert_day(["ok", "DRIFT", "ok", "DRIFT", "DRIFT", "DRIFT"]) == 5
    assert ops.first_alert_day(["DRIFT", "ok", "DRIFT", "ok"]) is None


def test_gate_rejects_worse_and_accepts_clearly_better():
    rng = np.random.default_rng(0); y = (rng.random(4000) < 0.3).astype(int)
    strong = np.clip(y * 0.35 + rng.random(4000) * 0.65, 0, 1); weak = rng.random(4000)
    assert not ops.should_promote(y, strong, weak)["promote"], "a random model must not replace a good one"
    assert ops.should_promote(y, weak, strong)["promote"], "a clearly better model must pass"
    assert not ops.should_promote(y, strong, strong)["promote"], "identical models give no gain"


def test_canary_is_sticky_and_roughly_5_percent():
    b = np.array([ops.canary_bucket(i) for i in range(20000)])
    assert (b == np.array([ops.canary_bucket(i) for i in range(20000)])).all()
    assert 0.04 < (b < 5).mean() < 0.06
''', encoding="utf-8")
(proj / "tests" / "test_service.py").write_text('''import importlib.util, json, os, sys
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
from fastapi.testclient import TestClient
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import churn_ops as ops


@pytest.fixture(scope="module")
def served(tmp_path_factory):
    d = tmp_path_factory.mktemp("svc")
    csv = d / "t.csv"; ops.make_customers(3000, seed=0).to_csv(csv, index=False)
    ops.train_and_track({"C": 0.05, "seed": 0, "test_size": 0.25}, csv, d / "model", f"sqlite:///{d / 'm.db'}")
    os.environ["MODEL_DIR"], os.environ["PRED_LOG"] = str(d / "model"), str(d / "pred.jsonl")
    spec = importlib.util.spec_from_file_location("svc_under_test", Path(__file__).resolve().parents[1] / "churn_service.py")
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return TestClient(mod.app), d


GOOD = {"tenure_months": 8.5, "monthly_spend": 47.0, "support_tickets": 4, "plan": "standard", "region": "north"}


def test_health_and_metadata(served):
    c, _ = served
    assert c.get("/health").json()["status"] == "ok" and "data_sha256" in c.get("/metadata").json()


@pytest.mark.parametrize("bad", [{**GOOD, "plan": "gold"}, {**GOOD, "tenure_months": -1}, {k: v for k, v in GOOD.items() if k != "region"}, {**GOOD, "monthly_spend": "lots"}])
def test_bad_input_is_rejected_before_the_model(served, bad):
    c, _ = served
    assert c.post("/predict", json=bad).status_code == 422


def test_parity_with_offline_pipeline(served):
    import joblib
    c, d = served
    frame = ops.make_customers(200, seed=9)[ops.NUM + ops.CAT]
    offline = joblib.load(d / "model" / "model.joblib").predict_proba(frame)[:, 1]
    online = np.array(c.post("/predict/batch", json={"customers": frame.to_dict("records")}).json()["churn_probability"])
    assert np.abs(online - offline).max() < 1e-5, "serving differs from training: check preprocessing"


def test_metrics_histogram_is_cumulative_and_consistent(served):
    c, _ = served
    for _ in range(5):
        c.post("/predict", json=GOOD)
    lines = [l for l in c.get("/metrics").text.splitlines() if l and not l.startswith("#")]
    buckets = [float(l.split()[1]) for l in lines if "_bucket" in l]
    count = float([l for l in lines if l.startswith("churn_request_latency_ms_count")][0].split()[1])
    assert buckets == sorted(buckets), "histogram buckets must be cumulative (never decrease)"
    assert buckets[-1] == count, "the +Inf bucket must equal the total count"


def test_every_prediction_is_logged_with_its_model_version(served):
    c, d = served
    n0 = len((d / "pred.jsonl").read_text(encoding="utf-8").splitlines()) if (d / "pred.jsonl").exists() else 0
    c.post("/predict", json=GOOD)
    lines = (d / "pred.jsonl").read_text(encoding="utf-8").splitlines()
    rec = json.loads(lines[-1])
    assert len(lines) == n0 + 1 and {"score", "model_version", "plan"} <= set(rec)
''', encoding="utf-8")
r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "-p", "no:warnings", "tests"], cwd=proj, capture_output=True, text=True, env={**os.environ, "MLFLOW_DISABLE_AGENT_HINT": "1"}, encoding="utf-8")
print("\n".join((r.stdout + r.stderr).strip().splitlines()[-6:]))
```
```text
..................                                                       [100%]
18 passed in 8.88s
```

Each test guards a failure from this chapter: an unreproducible run, a "reproduction" on silently changed data, a model folder the service cannot describe, a drift threshold that cries wolf (or is silent), an alert on a window too small to mean anything, a gate that promotes noise, a canary that is not sticky, a service that accepts garbage, a service that disagrees with training, and predictions that are not logged.

### 9.5 Extensions

1. **A scheduled monitor**: write `python -m churn_ops.monitor --log predictions.jsonl --out report.json` and run it daily from cron or a CI schedule. Exit with a non-zero code on `DRIFT` so the scheduler alerts.
2. **Shadow mode**: make the service score each request with both `@champion` and `@challenger`, return the champion's answer, and log both. Then compute the disagreement rate for a week before any canary.
3. **Prometheus and a dashboard**: run Prometheus and Grafana in two `pbtut-*` containers on `127.0.0.1`, scrape `/metrics`, and draw p95 latency and request rate (swe.09's observability tutorial).
4. **Delayed labels**: simulate a 30-day label delay: write a job that joins the prediction log with outcomes after 30 days and reports AUC by cohort week.
5. **Retraining trigger**: when `first_alert_day` fires, automatically launch `dvc repro` on the latest data and run the gate, but require a human to approve the promotion.

## 10. Common traps

1. **Unseeded training** and untracked seeds: the "same" run gives different numbers (1.2).
2. **A tracked parameter the code ignores.** The record says `seed=0` but a shuffle is unseeded. Test reproduction (2.4).
3. **Loading a pickle you did not make.** Pickles execute code; prefer safer formats or trusted registries (2.3).
4. **Git for big data**, or data changes that are not versioned: the same commit gives different models (3.1).
5. **Undeclared dependencies** in a pipeline: DVC cannot rerun what it was not told about (3.3).
6. **Promoting on a point estimate** ("0.003 higher") instead of an interval on a holdout used for no other decision (4.2).
7. **A canary that is not sticky**, or judged on a few hundred delayed labels (4.3).
8. **Re-implementing preprocessing in the API.** One artifact, one code path, and a parity test (6.2, 6.3).
9. **Features that use the future.** Point-in-time correctness (6.4).
10. **Unpinned environments**, even inside Docker; slow container builds blamed on the wrong layer (5.3).
11. **Alerting on p-values** with big windows, or on PSI with tiny windows. Set a minimum size and calibrate on no-drift windows (7.2).
12. **Treating a drift alert as proof of damage**, or silence as proof of health. Covariate drift can be harmless; concept drift is invisible to input monitors (7.4).
13. **No rollback plan:** keep the previous model folder and the previous alias target (4.2, 9.3).
14. **Monitoring the service but not the data**, or the data but not the outcomes (7.1).

## 11. Summary

- A trained model is the product of **code, data, configuration, environment and randomness**. MLOps records all five at every run, and **reproduces** a run by reading the record, refusing if the data's hash changed.
- **Experiment tracking** (MLflow): runs with parameters, metrics, tags and artifacts in a backend store plus an artifact store; `search_runs` as a DataFrame; model signatures; the registry with versions and movable **aliases** (`champion`); promotion and rollback are label moves.
- **Data and pipeline versioning** (DVC): content-addressed storage, tiny `.dvc` pointers in git, a remote with `push`/`pull`, time travel with `git checkout` + `dvc checkout`; `dvc.yaml` pipelines that rerun only stale stages from declared dependencies and parameters, with `params diff` and `metrics diff`.
- **Gates and releases**: compare a candidate with the champion on an untouched holdout with an **interval**, add guardrails (calibration, latency, slices); roll out with shadow, canary (sticky hash buckets) or blue/green, with rollback ready.
- **Serving**: load once, validate the input contract, return the model version, expose `/health`, `/metadata` and `/metrics`, log every prediction, batch when you can. Package with **Docker** from pinned, pre-downloaded wheels so the environment equals the training one.
- **Training-serving consistency**: skew is silent. One artifact with the preprocessing inside, a contract at the door, a **parity test**, logged inputs, and **point-in-time correct** features.
- **Monitoring**: three layers (service, data, model). Drift statistics (PSI, KS, chi-square) from scratch; significance is not size; calibrate thresholds and minimum window sizes on no-drift windows; covariate drift is not damage; concept drift needs outcomes; write the runbook first.
- **CI for ML**: tests for code, data (schema, nulls, ranges, duplicates, leakage), pipeline smoke, model floors and determinism, service contract and parity; the gate blocks a merge like a failing test.
- A finished project is a small tested package whose loop closes: track, serve, monitor, retrain, gate, release, roll back.

**Self-check (answer without looking back):**

1. Name the five ingredients needed to reproduce a trained model, and say which tool in this chapter stores each.
2. A teammate promotes a model because its AUC is 0.004 higher on the validation set used to tune it. List three things wrong with the decision.
3. Your service returns plausible scores but conversions fell after a deployment. What is "training-serving skew", and what two cheap checks would have caught it?
4. Why can a drift monitor on inputs be silent while the model gets worse?
5. With a window of 100 rows the PSI of a *stable* feature is often about 0.1. What does that imply for an alert threshold?
6. In a canary release, why must the traffic split be a function of the customer id and not a random choice per request?

<details><summary>Answer</summary>

1. Code (git), data (DVC pointer + hash), configuration including seed (`params.yaml`, MLflow params), environment (pinned `requirements.txt`, Docker image, MLflow `requirements.txt`), randomness (the seed, recorded as a parameter and actually used).
2. The validation set was used to tune, so it is optimistically biased and should not decide; there is no interval (0.004 is likely noise); no guardrails (calibration, latency, slices); no holdout from the current world; no shadow or canary; and no rollback plan stated.
3. Skew is a difference between how features are computed at training and at serving (units, category order, missing-value handling, future information). Catch it with a parity test (golden rows through the service vs the offline pipeline) and a contract plus monitoring of input distributions.
4. Concept drift changes the relationship between inputs and outcome without changing the inputs. Only outcomes (performance when labels arrive) reveal it.
5. Small windows are noisy, so a threshold of 0.1 would false-alarm constantly. Require a minimum window size and set the threshold from the no-drift distribution (for example above its 99th percentile for that window size).
6. A random split per request would show one customer both models over time, break the comparison, and make the experience inconsistent; a hash of the id (with a salt) is deterministic, sticky, reproducible and extendable (25% keeps the original 5%).

</details>
