## Hint 1

Why must the text you hash be *the same* every time, on every machine? Which `json.dumps` options remove the choices (spaces, key order) that would otherwise change the text?

## Hint 2

```text
text = json.dumps(values, sort_keys=True, separators=(",", ":"), allow_nan=False)
digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
return {"sha256": digest, "seed": seed, "params": copy.deepcopy(params), "python": platform.python_version(), "n": len(values)}
```
`allow_nan=False` turns NaN into a `ValueError` for you.
