# Config classes and a factory

Chapters 11 and 12. One codebase runs in three places (a developer's laptop, the tests, the production server) with different settings. In `solution.py` write:

- A base class `Config` with `SECRET_KEY = "change-me"`, `DEBUG = False`, `TESTING = False`, `PER_PAGE = 10` and a **mutable** setting `FEATURES = {"beta": False}`.
- `DevelopmentConfig(Config)`: `DEBUG = True`, `SECRET_KEY = "dev-key"`. `TestingConfig(Config)`: `TESTING = True`, `SECRET_KEY = "test-key"`. `ProductionConfig(Config)`: nothing extra.
- `create_app(name="development")` that builds a Flask app from the class registered under `"development"`, `"testing"` or `"production"`. An unknown name raises **`ValueError`**.
- For `"production"` the secret key comes from the environment variable `SECRET_KEY`. If it is **missing, empty or still `change-me`**, raise **`RuntimeError`**: a production server must never start with a known key.
- Every app must have **its own copy** of the settings: changing `app.config["FEATURES"]` of one app must not change another app **nor the class** `Config` (`from_object` copies references, not values).
- A route `GET /config` returns JSON `{"name": name, "debug": app.debug, "testing": app.testing, "per_page": <PER_PAGE>}`.

## Example

```python
app = create_app("testing")
app.config["SECRET_KEY"]      # "test-key"
create_app("production")       # RuntimeError unless SECRET_KEY is set in the environment
```
