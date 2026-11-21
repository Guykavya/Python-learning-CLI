## Hint 1

If you raise as soon as you find the first mistake, what does the person fixing the deployment have to do? Which Python structure lets you remember several problems and raise once at the end?

## Hint 2

```text
problems = []
database_url = env.get("DATABASE_URL") or ""          # "" and missing both mean "not set"
if not database_url: problems.append("DATABASE_URL is required")
elif "://" not in database_url: problems.append(...)
... the same for SECRET_KEY, PORT (try int(); check 1..65535), LOG_LEVEL (upper(); in the allowed set)
if problems: raise ConfigError("; ".join(problems))
```

For the password in `repr`, a regular expression like `(://[^:/@]+:)[^@]+(@)` replaced by `\1***\2` does it. Test it on a URL with and without a password.
