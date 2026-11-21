## Approach

```python
def load(path=None, env=None, flags=None):
    env = os.environ if env is None else env
    raw, sources, unknown = dict(DEFAULTS), {k: "default" for k in DEFAULTS}, []
    if path and Path(path).exists():
        for key, value in tomllib.loads(Path(path).read_text(encoding="utf-8")).items():
            if key in DEFAULTS:
                raw[key], sources[key] = value, "file"
            else:
                unknown.append(key)
    for key in DEFAULTS:
        value = env.get(ENV_PREFIX + key.upper(), "")
        if value != "":
            raw[key], sources[key] = value, "env"
    for key, value in (flags or {}).items():
        if key in DEFAULTS and value is not None:
            raw[key], sources[key] = value, "flag"

    def convert(name, fn):
        try:
            return fn(raw[name])
        except (ValueError, TypeError) as e:
            raise ValueError(f"{name} from {sources[name]}: {raw[name]!r} ({e})") from e

    settings = Settings(folder=convert("folder", lambda v: Path(str(v)).expanduser()),
                        keep_days=convert("keep_days", int),
                        dry_run=convert("dry_run", to_bool),
                        log_level=convert("log_level", _level),
                        api_token=env.get(ENV_PREFIX + "API_TOKEN") or None,
                        sources=sources)
    return settings, sorted(unknown)
```

Layering by **overwriting** makes the precedence obvious: the last layer applied is the strongest. Converting once, at the end, means environment strings (`"10"`, `"no"`) and TOML values (`10`, `false`) go through the same rules, and an error can say **where** the bad value came from, which is the first thing you need at 3 a.m. Reporting unknown keys turns a silent typo (`kep_days = 7`, ignored, so the default 30 is used) into a visible warning.

## Complexity

O(number of settings + keys in the file).

## Another way

Use a library: `pydantic-settings` (swe.05 uses pydantic) declares the same thing as a class with types, reads `.env` files and environment variables with a prefix, and validates. The rules you wrote here (precedence, empty means unset, secrets only from the environment) are the questions to check in its documentation.
