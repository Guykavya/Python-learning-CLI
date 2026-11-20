## Approach

Three layers, from the weakest to the strongest: code defaults, environment, explicit test settings.

```python
def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(PER_PAGE=10, TITLE="My Blog", DEBUG=False, FEATURES={"beta": False}, SECRET_KEY="dev")
    app.config.from_prefixed_env("BLOG")
    app.config.update(test_config or {})
    ...
```

Example: `BLOG_FEATURES__beta=true` is split at `__`: the key `FEATURES`, then the nested key `beta`, value `json.loads("true")` which is `True`. The existing dict is updated, not replaced: other keys of `FEATURES` stay.

Because the values are parsed as JSON, `BLOG_DEBUG=false` is the real `False`; with a plain `os.environ.get` you get the **string** `"false"`, which is truthy: a classic bug that turns debug mode *on*.

## Complexity

`O(number of variables in the environment)`.

## Another way

`python-dotenv` (Flask loads a `.env` file when it is installed) fills the environment from a file during development. The variable names stay the same in production, where the platform sets them.

## Not covered

A secret that *looks* like JSON (`BLOG_SECRET_KEY=12345`) becomes an **int**: a surprise for secrets made of digits. Use a random key with letters.
