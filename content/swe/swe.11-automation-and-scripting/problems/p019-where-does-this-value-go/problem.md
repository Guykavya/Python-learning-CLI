# Where does this value go?

Chapter section 8.1 (where settings live) and "Try it: where does this value go?". This uses the rules of problem p018's `load(path, env, flags)`:

- precedence, weakest first: **defaults < config file < environment `TIDY_*` < flags**;
- defaults: `folder="~/Downloads"`, `keep_days=30`, `dry_run=True`, `log_level="WARNING"`;
- an environment variable set to the **empty string** counts as not set;
- a flag whose value is `None` was **not typed** and changes nothing;
- `log_level` is upper-cased; `dry_run` strings are read with `to_bool` (`off` is `False`);
- `api_token` comes **only** from `TIDY_API_TOKEN`; an `api_token` in the file is ignored (and reported as unknown).

The situation on the server:

```toml
# tidy.toml
folder = "/data/inbox"
keep_days = 14
dry_run = false
log_level = "info"
api_token = "abc123"
```

```text
# environment of the cron job
TIDY_FOLDER=
TIDY_KEEP_DAYS=7
TIDY_LOGLEVEL=DEBUG
TIDY_DRY_RUN=off
```

```python
# what argparse produced from the command line `tidy --dry-run`
flags = {"keep_days": None, "dry_run": True, "log_level": None}
settings, unknown = load("tidy.toml", env=env, flags=flags)
```

For each of the five settings, what is its final value, and which layer did it come from?

## Answer format

Five lines, in this order, as `name = value (source)`, where source is one of `default`, `file`, `env`, `flag`. Write the folder with forward slashes, booleans as `True`/`False`, and a missing token as `None`:

```text
folder = ... (...)
keep_days = ... (...)
dry_run = ... (...)
log_level = ... (...)
api_token = ... (...)
```

## After you answer

- Which **one** line of the environment did someone mean to take effect, and why did it not? How would p018's `load` help you notice?
- `TIDY_DRY_RUN=off` was meant to make the nightly job do real work. Why does the job still only do a dry run?
