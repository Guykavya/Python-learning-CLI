# ChainMap: layered configuration

Real programs read settings from several places, with a clear priority: a command-line option
beats an environment variable, which beats the config file, which beats the built-in default.
Merging them with `{**defaults, **file_cfg, **env, **cli}` works once, but the result is a
frozen copy: you cannot tell where a value came from, and later changes to a layer are lost.

`collections.ChainMap(m1, m2, m3, ...)` is a **view** over several dicts. A lookup searches them
**in order** and returns the first hit. Writes and deletes only ever touch the **first** map.

Write three functions in `solution.py`.

1. `env_overrides(environ: Mapping[str, str], prefix: str = "APP_") -> dict[str, str]`
   - Keep only the keys that start with `prefix`; the new key is the rest of the name,
     lower-cased: `APP_DEBUG` → `debug`. Values stay strings. Other keys are ignored.
2. `build_config(defaults: dict, file_cfg: dict, env: dict, cli: dict) -> ChainMap`
   - Priority, highest first: **runtime**, `cli`, `env`, `file_cfg`, `defaults`. *runtime* is a new
     empty dict that you put in front, so that `config[key] = value` at run time never changes
     any of the caller's dicts.
   - `cli` comes from `argparse`, which sets options the user did not give to `None`. Leave out
     the `cli` entries whose value is `None` (so they do not hide lower layers).
   - The other layers must stay **live**: if the caller changes `defaults` later, the config sees it.
3. `source_of(config: ChainMap, key) -> str`
   - The name of the layer the value comes from: `"runtime"`, `"cli"`, `"env"`, `"file"` or
     `"defaults"`. A missing key raises `KeyError`.

Do not read the real `os.environ` in these functions; the caller passes it in.

**Example**

```python
defaults = {"host": "localhost", "port": 8000, "debug": False}
file_cfg = {"port": 9000}
env = env_overrides({"APP_DEBUG": "1", "HOME": "/home/k"})    # {'debug': '1'}
cli = {"port": 7000, "host": None}

cfg = build_config(defaults, file_cfg, env, cli)
cfg["port"], cfg["host"], cfg["debug"]     # (7000, 'localhost', '1')
source_of(cfg, "host")                     # 'defaults'  (cli host was None)
cfg["port"] = 1
source_of(cfg, "port")                     # 'runtime'
cli["port"]                                # 7000: the caller's dict is untouched
```
