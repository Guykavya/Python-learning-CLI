# Problem plan: ml.06 MLOps (30 problems)

Rules: [README.md](README.md), table format of [dsa.07-problem-plan.md](dsa.07-problem-plan.md), **ml track notes M1–M5 in
[ml.01-problem-plan.md](ml.01-problem-plan.md)**. Function style. Ids `ml.06.p001`…`p030`.
**Mix:** 9 drill, 13 applied, 6 deep, 2 challenge. **Kinds:** 22 code, 4 trace, 4 explain.
**assessment:** explain = p027, trace = p025, fix = p022, build = p030.
**★ core set (12):** p2, p4, p5, p6, p9, p14, p19, p22, p24, p27, p28, p30.

## Testing notes

- **No torch in this module.** Models are scikit-learn pipelines on the chapter's synthetic customers (`make_customers(n, seed, spend_shift,
  premium_boost, concept)`, copied into `conftest.py`). sklearn + pandas + mlflow fit under the cap without torch (VmPeak 860 MB at import).
- **MLflow (3.x):** the plain file store (`file:` URI, `./mlruns`) now raises "filesystem tracking backend is in maintenance mode" unless
  `MLFLOW_ALLOW_FILE_STORE=true`. Use SQLite: `mlflow.set_tracking_uri("sqlite:///" + (tmp_path / "mlflow.db").as_posix())`.
  Measured under the cap: params + metrics + step history + `log_dict` + `search_runs(output_format="list")` 4.6 s, VmPeak 735 MB;
  plus a pickled `LogisticRegression` via `log_artifact` and `download_artifacts` 5.4 s, VmPeak 930 MB.
  **`mlflow.sklearn.log_model` fails under the cap** ("failed to map segment from shared object") → never use mlflow model flavours in
  tests; log a pickle with `log_artifact`. Params come back as **strings** (`{'lr': '0.1', 'C': '1.0'}`), metrics as floats: p7 and p8 use this.
- **DVC 3.67:** the CLI works in `tmp_path` (`dvc init --no-scm`: 0.8 s; `dvc add data.csv`: 1.0 s, 74 MB). The `md5` in a `.dvc` file is the
  plain md5 of the file's bytes (checked with LF and CRLF files). The `.dvc` file is YAML: `outs: [{md5, size, hash: md5, path}]`.
  Problems reimplement the logic; at most one test (p10) also compares with the real CLI, found next to `sys.executable`
  (`Path(sys.executable).with_name("dvc")`, `dvc.exe` on Windows), skipped per test only if missing.
- **Docker is never run.** p21 lints Dockerfile text.
- FastAPI with `TestClient`; the model is injected into `create_app(model, reference)` (R1). fastapi + sklearn VmPeak not measured
  (expect < 900 MB; check on the first serving problem).
- Reuse the chapter's names: `file_sha256`, `RunHandle`, `tracked_run`, `reproduce`, `reproduce_mlflow`, `ContentStore`, `auc_gain`, `ece`,
  `p95_latency_ms`, `gate`, `bucket(customer_id, salt)`, `Customer`, `BatchRequest`, `reimplemented`, `assert_parity`, `psi_numeric`,
  `psi_categorical`, `Reference`, `drift_report`, `data_checks`, `read_prediction_log`, `first_alert_day`, `should_promote`, `train_and_track`.

## A. Why MLOps: reproducibility (Ch. 1)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 1 | Why the same code gives two answers | drill | explain | seeds, data version, library versions, hidden state, code version; checklist of 5 sources |
| 2 | Hash a data file | drill | code | `file_sha256(path, n)` reads in chunks; equals `hashlib.sha256(bytes)` on a 3 MB file; LF and CRLF files differ; first `n` hex characters |
| 3 | An environment fingerprint | drill | code | `env_record(packages)` → Python version, platform, versions via `importlib.metadata`; a missing package gives `None`, not an exception |

## B. Experiment tracking (Ch. 2)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 4 | A run record by hand | applied | code | `tracked_run(root, name, params, data_file)` writes `run.json` (params, metrics, data hash, env) in a new run folder; returns a `RunHandle`; two runs never share a folder |
| 5 | Reproduce a past run | applied | code | `reproduce(root, run_id, data_path)` refits from the record and returns the same metrics; a changed data file raises `ValueError` naming both hashes |
| 6 | MLflow: log and search | applied | code | SQLite backend in `tmp_path`; log params, a metric per step, a dict artifact; `best_run(experiment, metric)` via `search_runs(output_format="list")` |
| 7 | What MLflow gives back | drill | trace | `⚠ HAND-TRACE` after logging `lr=0.1`, `epochs=3`, `use_bias=True` and a loss at steps 0–4, print the params dict and the latest metric; types matter (strings); verify the exact `True` spelling by running it |
| 8 | Reproduce from MLflow | deep | code | `reproduce_mlflow(run_id, data_path, tracking_uri)` converts params back to their types, checks the data-hash tag, loads the pickled model artifact; predictions equal the original |

## C. Versioning data and pipelines (Ch. 3)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 9 | A content-addressed store | applied | code | `ContentStore(root).put(path)` → md5; stored at `ab/cdef…`; the same content is stored once; `get(md5, dest)` restores bytes; unknown hash raises |
| 10 | The `.dvc` pointer file | drill | code | `write_pointer(path)` / `read_pointer(dvc_file)` with `outs: [{md5, size, hash, path}]`; md5 equals DVC's (plain md5); one test compares with real `dvc add` in `tmp_path` |
| 11 | Which stages rerun? | deep | trace | `⚠ HAND-TRACE` a 4-stage `dvc.yaml` (deps/outs) and a lock file; one input file changed; print the stages that rerun, in order |
| 12 | Stage planning | challenge | code | `stages_to_run(stages, current_hashes, lock)`: changed deps rerun and everything downstream; topological order; a cycle raises naming a stage on it |

## D. Registry, promotion, safe release (Ch. 4)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 13 | A registry with aliases | drill | trace | `⚠ HAND-TRACE` a sequence of `register`, `set_alias("champion")`, `promote`, `rollback` on the chapter's tiny registry; print versions and aliases after each |
| 14 | The promotion gate | applied | code | `gate(champ, cand, X, y, min_gain, max_ece, max_latency_ms)` → (bool, reasons); every failing rule appears in `reasons`; latency measured with an injected clock |
| 15 | Bootstrap gain | deep | code | `auc_gain(y, p_champ, p_cand, n_boot, seed)` paired bootstrap; identical models → interval [0, 0]; `should_promote` needs the lower bound > `min_gain` |
| 16 | Stable canary buckets | applied | code | `bucket(customer_id, salt)` → 0–99 from sha256, not `hash()`; ~10% for a 10% canary over 10,000 ids; the same bucket in a child process with a different `PYTHONHASHSEED` (`sys.executable`) |
| 17 | Shadow, canary or rollback? | drill | explain | when each is the right move; what each one protects against; checklist of 3 cases |

## E. Serving (Ch. 5)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 18 | The request schema | drill | code | pydantic `Customer` with ranges, an enum for the plan, extra fields forbidden; through `TestClient` a bad request gets 422 naming the field |
| 19 | `/predict` and `/predict_batch` | applied | code | `create_app(model)` with `/health`, `/metadata`, `/predict`, `/predict_batch`; batch scores equal single scores; metadata has the model version and data hash |
| 20 | Latency metrics | applied | code | `LatencyRecorder` keeps the last N latencies; nearest-rank p50/p95; `/metrics` returns the chapter's text format |
| 21 | Review a Dockerfile | deep | code | `dockerfile_problems(text)` → list of rule ids: base image `latest` or no tag, requirements copied after the code (cache busting), running as root, no `--no-cache-dir`, model baked from a path outside the context; 6 Dockerfiles in the test; Docker is not run |

## F. Training-serving consistency (Ch. 6)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 22 | Fix the serving features | applied | code | `assessment = "fix"`; the given serving code re-implements preprocessing with spend in cents and a different column order; `assert_parity(client, frame, offline_scores, atol=1e-5)` fails until fixed (fix by reusing the training pipeline) |
| 23 | Time leakage | deep | explain | a feature computed with data from after the prediction time; why offline scores look great; how to catch it (point-in-time joins, time splits); checklist of 4 points |

## G. Monitoring and drift (Ch. 7)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 24 | PSI for a numeric feature | drill | code | `psi_numeric(ref, cur, edges, eps)` with edges from the reference quantiles; identical samples → 0; a hand-checked 3-bin case |
| 25 | PSI by hand | applied | trace | `assessment = "trace"`; `⚠ HAND-TRACE` 3 bins with reference shares 0.5/0.3/0.2 and current 0.3/0.3/0.4: each term and the total (`:.4f`) |
| 26 | PSI for categories, including new ones | applied | code | `psi_categorical(ref_shares, cur_values, eps)`; a category unseen in the reference is counted, not dropped; eps avoids `log(0)` |
| 27 | Drift is not damage | deep | explain | `assessment = "explain"`; input drift vs performance decay; delayed labels; why to watch outcomes and scores too; checklist of 4 points |
| 28 | The first alert day | applied | code | `drift_report(ref, window, scores, min_rows, psi_alert)` per day and `first_alert_day(statuses, consecutive)`; small windows are "insufficient", not alerts; drift injected from day 15 alerts on day 15–17 |

## H. CI for ML (Ch. 8)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 29 | Data checks before training | applied | code | `data_checks(d, ref, max_null, leak_corr)` → list of failures: missing or extra columns, null share above the limit, a column correlated > 0.95 with the target (leak) |

## I. Project: deploy and monitor a model as a service (Ch. 9)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 30 | Build: model service with drift monitoring | challenge | code | `assessment = "build"`; `train_and_track` (MLflow, SQLite in `tmp_path`) → `create_app` → JSONL prediction log → `read_prediction_log` → `drift_report`; the test sends 30 days of traffic with `spend_shift` from day 15 and expects the first alert on day 15–17, and `reproduce` of the tracked run to give the same scores; ≤ 20 s |

## Counts check

Tiers: drill 1, 2, 3, 7, 10, 13, 17, 18, 24 = 9; applied 4, 5, 6, 9, 14, 16, 19, 20, 22, 25, 26, 28, 29 = 13; deep 8, 11, 15, 21, 23, 27 = 6;
challenge 12, 30 = 2. Total 30.
Trace (4): 7, 11, 13, 25. Explain (4): 1, 17, 23, 27. Code: 22. One of each assessment: 27, 25, 22, 30.

## Risks and open questions

- p30 combines MLflow + sklearn + FastAPI + pandas: VmPeak could pass 1 GiB. Measure the reference first; if it fails, track with the
  hand-made run record (p4) instead of MLflow in the build.
- p10's real-DVC test needs the `dvc` executable; on a machine without it that one test is skipped (others still run).
- MLflow prints progress bars ("Downloading artifacts") to stderr: harmless, but pass `MLFLOW_ENABLE_ARTIFACTS_PROGRESS_BAR=false` in conftest if noisy (not verified).
