# Keep secrets out of the logs

Chapter section 15.6 (logging for security) and "Try it: the logged password". Logs are copied around and kept for months, so a password or token that reaches a log is leaked. The best defence is never to log secrets; a **redaction filter** is the safety net that catches the mistakes.

Write a `logging.Filter` called `RedactSecrets`. Attached to a logger, it rewrites every record **before** any handler sees it.

```python
class RedactSecrets(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool: ...
```

The sensitive names are `password`, `token`, `authorization` and `api_key` (any capital letters: `Password`, `Authorization`). The replacement text is `[REDACTED]`.

**Rules**

1. **Dictionary arguments.** If a log argument is a `dict`, every value whose **key** is a sensitive name (compare the key in lower case, exactly) is replaced by `"[REDACTED]"`. This works for nested dictionaries and for dictionaries inside lists. The caller's own dictionary must **not** be changed: build a copy. This covers both `log.info("login %s", {"user": "asha", "password": "x"})` and `log.info("%(user)s %(password)s", {...})`.
2. **Text of the form `name=value`.** In the formatted message, for each sensitive name written as `name=value`, replace the value by `[REDACTED]`. The name is case-insensitive and must stand alone (not inside a longer word), and the value runs up to the next space, comma, `&` or `;`. A value that starts with `Bearer ` takes the word after it too (`authorization=Bearer abc.def`).
3. The record must **still be logged**, with the rest of the message unchanged. `filter` returns `True`.
4. After your work the record holds the finished text, so a handler does not format it again (set `record.msg` to the final message and `record.args` to `None`).

## Example

```text
log.warning("login failed for ada, password=hunter2 from 10.0.0.9")
   -> login failed for ada, password=[REDACTED] from 10.0.0.9
log.info("sending %s", {"user": "asha", "Token": "abc123", "meta": {"api_key": "k-1"}})
   -> sending {'user': 'asha', 'Token': '[REDACTED]', 'meta': {'api_key': '[REDACTED]'}}
log.info("GET /search?q=books&token=abc123&page=2")
   -> GET /search?q=books&token=[REDACTED]&page=2
log.info("order 17 cancelled by user 1")                     (unchanged)
```

The tests attach your filter to a logger and read the result with pytest's `caplog`. They import `RedactSecrets`.
