## Hint 1

When does a `logging.Filter` run, and what can it change? It receives the **record** before the handlers format it. Which two attributes hold the text and the arguments of the message? What does `record.getMessage()` give you?

## Hint 2

There are two separate jobs. **Job A:** the arguments. Python's `logging` puts a single dict argument into `record.args` itself (not inside a tuple), so look at both shapes. Write a small recursive helper `_clean(value)` that returns a **copy**: dict -> new dict with sensitive keys masked, list or tuple -> new list or tuple of cleaned items, anything else -> as it is. **Job B:** the text. After formatting with `getMessage()`, a regular expression finds `name=value`. Write it with `(?<!\w)` in front of the name so `mytoken=5` is not touched, and `=` right after the name so `password_age=40` is not touched.

## Hint 3

```text
_clean(value):
    dict   -> {key: MASK if str(key).lower() in SENSITIVE else _clean(item)}
    list/tuple -> same type of cleaned items
    other  -> value

filter(record):
    if record.args: record.args = _clean(record.args)
    message = record.getMessage()
    record.msg = REGEX.sub(name + "=" + MASK, message)      # (?i)(?<!\w)(password|token|authorization|api_key)=(?:bearer\s+)?[^\s,&;]+
    record.args = None
    return True
```
