## Hint 1

`hmac.new` takes three things: the key (bytes), the message (bytes) and the hash algorithm.
Which of your values are `str` and need `.encode("utf-8")`? For `load_secret`, why is
`env.get(NAME, "")` handier than `env[NAME]`, and what should the function do for the three bad
cases: missing, empty after `strip()`, too short?

## Hint 2

```
load_secret(env=None):
    if env is None: env = os.environ          # looked up at call time
    value = env.get("PAGEBOUND_PSEUDO_KEY", "").strip()
    if value == "": raise RuntimeError("PAGEBOUND_PSEUDO_KEY is not set ...")
    if len(value) < 16: raise RuntimeError("PAGEBOUND_PSEUDO_KEY is too short ...")   # no value!
    return value.encode("utf-8")

pseudonymise(value, key):
    if value is None: return None
    text = value.strip().lower()
    return hmac.new(key, text.encode("utf-8"), hashlib.sha256).hexdigest()[:16]

pseudonymise_rows(rows, key, field, out_field):
    for each row: copy items into a new dict, but put out_field -> pseudonym where field was
                  if field missing: new[out_field] = None
```
