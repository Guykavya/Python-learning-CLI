## Hint 1

Which keys of `Config` must always be there, and which may be missing? If `total=False` makes **every** key of its class optional, how can one class have both required and optional keys? (Two classes, or a per-key marker.)

## Hint 2

For a mix, either inherit: a base class with the required keys and a subclass with `total=False` for the optional ones; or mark each optional key with `NotRequired[...]`. `Patch` has no required key at all, so one class with `total=False` is enough. In the functions, use `in` to ask "is the key present?" (not `.get()` with truthiness: `debug=False` is present).

## Hint 3

```
class Config(TypedDict):     host: str ; port: int ; debug: NotRequired[bool] ; timeout: NotRequired[float]
class Patch(TypedDict, total=False):  host, port, debug, timeout

with_defaults(cfg):  out = {**cfg}; out.setdefault("debug", False); out.setdefault("timeout", 30.0); return out
apply_patch(cfg, patch):  return {**cfg, **patch}
describe(cfg):  text = f"{cfg['host']}:{cfg['port']}"
                if cfg.get("debug") is True: text += " (debug)"
                if "timeout" in cfg: text += f" timeout={cfg['timeout']}"
```
