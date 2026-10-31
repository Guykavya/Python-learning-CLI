## Hint 1

`ChainMap(a, b, c)` looks in `a`, then `b`, then `c`. So the arguments go in priority order, highest first. Where must the new empty runtime dict go so that assignments land in it? And which layer needs a filtered **copy** instead of the original dict?

## Hint 2

`config.maps` is the list of the dicts in search order. If you always build the ChainMap with the five layers in the same order, the index of the first map that contains the key tells you the layer name. For the env: `key.startswith(prefix)` and `key[len(prefix):].lower()`.

## Hint 3

```
LAYERS = ("runtime", "cli", "env", "file", "defaults")

build_config(defaults, file_cfg, env, cli):
    cli_given = {k: v for k, v in cli.items() if v is not None}
    return ChainMap({}, cli_given, env, file_cfg, defaults)

source_of(config, key):
    for name, layer in zip(LAYERS, config.maps):
        if key in layer: return name
    raise KeyError(key)
```
