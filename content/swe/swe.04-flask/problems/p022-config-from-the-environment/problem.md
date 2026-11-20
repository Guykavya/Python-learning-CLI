# Config from the environment

Chapter section 12.2. Settings that change **per machine** (a secret key, the page size, a feature flag) belong in environment variables, not in the code. Flask can read them: `app.config.from_prefixed_env("BLOG")` takes every variable that starts with `BLOG_`, removes the prefix and **parses the value as JSON when it can** (`true`, `20`, `0.5`, `["a"]`), otherwise it keeps the string.

In `solution.py` write `create_app(test_config=None)`:

1. Start with the defaults `PER_PAGE=10`, `TITLE="My Blog"`, `DEBUG=False`, `FEATURES={"beta": False}`, `SECRET_KEY="dev"`.
2. Read the environment with `app.config.from_prefixed_env("BLOG")`. Then the tests set `BLOG_DEBUG=false`, `BLOG_PER_PAGE=20`, `BLOG_TITLE=Hello World`, `BLOG_FEATURES__beta=true` (a **double underscore** means a nested key) and expect `False`, `20`, `"Hello World"`, `{"beta": True}`.
3. `test_config` (a dict) is applied **last**, so it wins over the environment.
4. `GET /settings` returns `{"per_page", "title", "debug", "features"}` as JSON.

Variables without the prefix (`DEBUG=1`, `PER_PAGE=5`) must be ignored.

## Example

```text
BLOG_PER_PAGE=20            -> app.config["PER_PAGE"] == 20     (an int, not "20")
BLOG_DEBUG=false            -> app.config["DEBUG"] is False
BLOG_FEATURES__beta=true    -> app.config["FEATURES"] == {"beta": True}
PER_PAGE=5 (no prefix)      -> ignored
```
