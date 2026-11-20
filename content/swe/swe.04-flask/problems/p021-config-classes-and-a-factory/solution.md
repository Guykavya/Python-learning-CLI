## Approach

```python
import copy
import os


def create_app(name="development"):
    if name not in CONFIGS:
        raise ValueError(f"unknown configuration {name!r}; choose one of {sorted(CONFIGS)}")
    config_class = CONFIGS[name]
    app = Flask(__name__)
    values = {key: getattr(config_class, key) for key in dir(config_class) if key.isupper()}
    app.config.from_mapping(copy.deepcopy(values))
    if name == "production":
        key = os.environ.get("SECRET_KEY", "")
        if not key or key == Config.SECRET_KEY:
            raise RuntimeError("Set the SECRET_KEY environment variable ...")
        app.config["SECRET_KEY"] = key
    ...
```

(The full file, with the classes and the `/config` route, is `reference.py`.)

Example: `dir(TestingConfig)` includes the upper-case names inherited from `Config`, so `PER_PAGE` and `FEATURES` come along. `deepcopy` gives each app its own `FEATURES` dict.

**Fail at startup.** `create_app("production")` raises before any request is served: a deployment with a missing or default key stops immediately and loudly, which is far better than running with a key that is in the Git history.

**Why copy?** `from_object` stores the same dict object that the class holds. Two apps (or two tests) would then change each other's settings *through the class*, a bug that appears only when the tests run in a certain order.

## Complexity

`O(number of settings)`.

## Another way

Read all settings from the environment (`app.config.from_prefixed_env`, problem 22) and keep only defaults in code: the twelve-factor way. Use config classes when the settings differ by *kind of run* and the environment for what differs by *machine* (database URL, secrets).

## Not covered

The instance folder and `app.config.from_pyfile` for settings kept outside Git.
