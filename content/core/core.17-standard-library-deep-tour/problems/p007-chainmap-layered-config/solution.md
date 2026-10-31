## Approach

A `ChainMap` stores a list of dicts, `config.maps`, and searches them in order. That makes the
priority order the **argument order**: `ChainMap(runtime, cli, env, file_cfg, defaults)`.

- **Writes go to the first map.** Putting a fresh `{}` first gives a safe place for run-time
  changes; no caller dict is ever modified, and deleting a runtime value uncovers the lower
  layers again.
- **Views stay live.** `env`, `file_cfg` and `defaults` are passed as they are, so later
  changes to them show through.
- **The cli layer is the exception.** `argparse` fills options the user did not pass with `None`,
  and a `None` in a higher layer would hide a real value below it. So the cli layer is a
  filtered copy.

`source_of` walks `config.maps` together with the fixed layer names and returns the first layer
that contains the key, which is exactly the rule ChainMap itself uses for lookups.

## Code

```python
from collections import ChainMap
from collections.abc import Mapping

LAYERS = ("runtime", "cli", "env", "file", "defaults")


def env_overrides(environ: Mapping[str, str], prefix: str = "APP_") -> dict[str, str]:
    result = {}
    for key, value in environ.items():
        if key.startswith(prefix):
            result[key[len(prefix):].lower()] = value
    return result


def build_config(defaults: dict, file_cfg: dict, env: dict, cli: dict) -> ChainMap:
    cli_given = {key: value for key, value in cli.items() if value is not None}
    return ChainMap({}, cli_given, env, file_cfg, defaults)


def source_of(config: ChainMap, key) -> str:
    for name, layer in zip(LAYERS, config.maps):
        if key in layer:
            return name
    raise KeyError(key)
```

In a real program you would call `env_overrides(os.environ)`. Taking it as a parameter keeps the
function easy to test.

## Complexity

A lookup is O(L) for L layers (here 5). Building is O(size of cli). No merged copy is made.

## Another way

`{**defaults, **file_cfg, **env, **cli_given}` gives the same values at build time: later
dicts win. It is simpler when nothing changes afterwards, but you lose `source_of`, live layers and
the safe runtime layer. `ChainMap.new_child()` is another tool: it returns a new ChainMap with an
empty dict added in front, which is how you would add a temporary override (for one request or one
test) and throw it away afterwards.
