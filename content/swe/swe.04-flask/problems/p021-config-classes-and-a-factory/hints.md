## Hint 1

Which operations can go wrong when you build the app: a name you do not know, a missing key in the environment? Where does it make sense to fail: at startup, or when the first user arrives?

## Hint 2

`app.config.from_object(cls)` reads the upper-case attributes of the class but does **not copy** mutable values. Build a dict of the upper-case attributes yourself and use `copy.deepcopy` on it, then `app.config.from_mapping(...)`. Read the key with `os.environ.get("SECRET_KEY", "")`.

## Hint 3

```text
if name not in CONFIGS: raise ValueError
values = {k: getattr(cls, k) for k in dir(cls) if k.isupper()}
app.config.from_mapping(copy.deepcopy(values))
if name == "production":
    key = os.environ.get("SECRET_KEY", "")
    if not key or key == Config.SECRET_KEY: raise RuntimeError(...)
    app.config["SECRET_KEY"] = key
```
