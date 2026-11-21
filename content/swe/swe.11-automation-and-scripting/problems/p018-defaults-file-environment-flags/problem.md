# Defaults, file, environment, flags

Chapter section 8.1 (where settings live) and "Try it: where does this value go?". A value that can change does not belong in the code. Settings come from four places, and the **stronger one wins**:

```text
defaults in the code  <  config file (TOML)  <  environment TIDY_*  <  command-line flags
```

The chapter's `load(path=None, env=None)` handles file and environment. Extend it with flags, convert types, report unknown keys, and remember where each value came from.

## What to write

The starter gives `DEFAULTS`, the frozen dataclass `Settings` and the helper names. Write:

```python
def to_bool(value) -> bool: ...
def load(path=None, env=None, flags=None) -> tuple[Settings, list[str]]: ...
```

Rules for `load`:

1. Start from `DEFAULTS` (`folder="~/Downloads"`, `keep_days=30`, `dry_run=True`, `log_level="WARNING"`), source `"default"`.
2. If `path` is given **and the file exists**, read it with `tomllib`; each known key overrides the default (source `"file"`). Every other key in the file is **not used** and its name goes into the returned list of unknown keys, sorted. (`api_token` in the file is reported too: secrets come from the environment only.) A missing file is not an error.
3. Environment (`env`, a dict; `None` means `os.environ`): `TIDY_FOLDER`, `TIDY_KEEP_DAYS`, `TIDY_DRY_RUN`, `TIDY_LOG_LEVEL` override (source `"env"`). A variable set to the **empty string counts as not set**.
4. Flags (`flags`, a dict such as `{"keep_days": 7, "dry_run": None}`, as argparse would give it): every key whose value is **not `None`** overrides (source `"flag"`).
5. Convert after choosing: `folder` to `Path(...).expanduser()`, `keep_days` to `int`, `dry_run` with `to_bool`, `log_level` upper-cased and one of `DEBUG`, `INFO`, `WARNING`, `ERROR`. A value that cannot be converted raises `ValueError` whose message names the setting **and** its source (for example `keep_days from env: 'ten'`).
6. `api_token` comes only from `TIDY_API_TOKEN` (empty means `None`). It is declared with `repr=False`, so printing the settings never shows it.
7. Fill `settings.sources`, a dict mapping each of the four setting names to `"default"`, `"file"`, `"env"` or `"flag"`.

`to_bool` accepts a real `bool`, or the strings `1 true yes on` / `0 false no off` in any case; anything else is a `ValueError`.

## Example

```toml
# tidy.toml
folder = "/data/inbox"
keep_days = 14
kep_days = 7            # typo
```

```python
s, unknown = load("tidy.toml", env={"TIDY_KEEP_DAYS": "10"}, flags={"dry_run": False, "keep_days": None})
s.folder, s.keep_days, s.dry_run, s.log_level    # (Path('/data/inbox'), 10, False, 'WARNING')
s.sources    # {'folder': 'file', 'keep_days': 'env', 'dry_run': 'flag', 'log_level': 'default'}
unknown      # ['kep_days']
```
