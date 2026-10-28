from typing import NotRequired, TypedDict


class Config(TypedDict):
    host: str
    port: int
    debug: NotRequired[bool]
    timeout: NotRequired[float]


class Patch(TypedDict, total=False):
    host: str
    port: int
    debug: bool
    timeout: float


def with_defaults(cfg: Config) -> Config:
    out = Config(host=cfg["host"], port=cfg["port"])
    out["debug"] = cfg.get("debug", False)
    out["timeout"] = cfg.get("timeout", 30.0)
    return out


def apply_patch(cfg: Config, patch: Patch) -> Config:
    out = Config(host=cfg["host"], port=cfg["port"])
    if "debug" in cfg:
        out["debug"] = cfg["debug"]
    if "timeout" in cfg:
        out["timeout"] = cfg["timeout"]
    if "host" in patch:
        out["host"] = patch["host"]
    if "port" in patch:
        out["port"] = patch["port"]
    if "debug" in patch:
        out["debug"] = patch["debug"]
    if "timeout" in patch:
        out["timeout"] = patch["timeout"]
    return out


def describe(cfg: Config) -> str:
    text = f"{cfg['host']}:{cfg['port']}"
    if cfg.get("debug") is True:
        text += " (debug)"
    if "timeout" in cfg:
        text += f" timeout={cfg['timeout']}"
    return text
