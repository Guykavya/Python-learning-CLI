## Approach

```python
SENSITIVE = {"password", "token", "authorization", "api_key"}
MASK = "[REDACTED]"
_TEXT = re.compile(r"(?i)(?<!\w)(password|token|authorization|api_key)=(?:bearer\s+)?[^\s,&;]+")


def _clean(value):
    if isinstance(value, dict):
        return {key: MASK if str(key).lower() in SENSITIVE else _clean(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return type(value)(_clean(item) for item in value)
    return value


class RedactSecrets(logging.Filter):
    def filter(self, record):
        if record.args:
            record.args = _clean(record.args)
        message = record.getMessage()
        record.msg = _TEXT.sub(lambda m: m.group(1) + "=" + MASK, message)
        record.args = None
        return True
```

Walk through the two jobs:

1. **Structured data first.** A dictionary logged with `%s` prints as `{'password': 'x'}`, which the `name=value` regex would miss. So the filter masks the dictionary values **by key** before the message is formatted. The copy matters: the dictionary belongs to the caller, who may still use it.
2. **Text second.** After `getMessage()` the arguments are folded into the string, and the regex masks `name=value`. The lookbehind `(?<!\w)` and the literal `=` keep the filter from touching `tokens=3` or `password_age=40`. `(?:bearer\s+)?` makes `authorization=Bearer abc.def` lose the token, not only the word `Bearer`.
3. **Finish the record.** The text is final, so `record.args = None` stops handlers from applying `%` formatting a second time (a `%` in a masked value would otherwise break).

`filter` returns `True`: the record is still logged. Returning `False` would drop the line, which hides the very event you want to see. The chapter's own filter (15.6) has the same shape; this version adds the dictionary handling.

Remember the chapter's warning: a filter is a **safety net, not a licence**. The real fix for the "logged password" mistake is not to put the password in the message at all.

## Complexity

`O(size of the arguments + length of the message)` per record: one pass over nested data and one regex pass.

## Another way

Give each secret a type: wrap passwords and tokens in a `Secret` class whose `__repr__` and `__str__` return `"[REDACTED]"`. Then `log.info("%s", secret)` is safe by construction, without any regex. Frameworks such as Pydantic use `SecretStr` for the same reason. The filter and the type work well together: the type stops the common mistakes, the filter catches the rest.
