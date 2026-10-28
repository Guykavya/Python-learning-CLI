from collections import ChainMap
from collections.abc import Mapping


def env_overrides(environ: Mapping[str, str], prefix: str = "APP_") -> dict[str, str]:
    return {}


def build_config(defaults: dict, file_cfg: dict, env: dict, cli: dict) -> ChainMap:
    return ChainMap()


def source_of(config: ChainMap, key) -> str:
    return "defaults"
