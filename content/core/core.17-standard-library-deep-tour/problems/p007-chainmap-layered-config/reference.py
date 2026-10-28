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
