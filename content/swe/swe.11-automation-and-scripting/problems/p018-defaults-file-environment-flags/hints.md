## Hint 1

Do not write four nested `if`s per setting. Keep two dictionaries, `raw` (name to the chosen value, still unconverted) and `sources` (name to where it came from), and apply the four layers in order from weakest to strongest; each layer simply overwrites both entries. Convert only at the end, once, so the error message can say which layer gave the bad value.

## Hint 2

```text
raw = dict(DEFAULTS); sources = {k: "default" for k in DEFAULTS}
if path and Path(path).exists():
    data = tomllib.loads(text)
    for k, v in data.items(): if k in DEFAULTS: raw[k] = v; sources[k] = "file"   else: unknown.append(k)
for k in DEFAULTS: v = env.get("TIDY_" + k.upper(), ""); if v != "": raw[k] = v; sources[k] = "env"
for k, v in (flags or {}).items(): if k in DEFAULTS and v is not None: raw[k] = v; sources[k] = "flag"
try: convert each -> except (ValueError, TypeError): raise ValueError(f"{name} from {sources[name]}: {raw[name]!r}")
return Settings(..., api_token=env.get("TIDY_API_TOKEN") or None, sources=sources), sorted(unknown)
```
