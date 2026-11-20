## Hint 1

Environment variables are always **strings**. Which Flask method converts them for you, and what prefix do you give it?

## Hint 2

`app.config.from_prefixed_env("BLOG")` goes after the defaults (so it can override them) and before `test_config` (so tests can override it). Flask decides the types: it tries `json.loads` on every value.

## Hint 3

```text
app.config.update(defaults)
app.config.from_prefixed_env("BLOG")
app.config.update(test_config or {})
```
