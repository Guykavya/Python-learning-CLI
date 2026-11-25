## Hint 1

Which cases are "missing" and which are "wrong"? What should `parse_number("-")` give, and what should `parse_number("-5")` give? Does the order of rules 2 and 3 matter?

## Hint 2

```text
t = text.strip().lower()
if t in MISSING: return None
for junk in ("rs.", "rs", "ms", "%", "$"): t = t.replace(junk, "")
t = t.replace(",", "").replace(" ", "")
try: x = float(t)
except ValueError: raise ValueError(f"cannot parse {text!r}")
if not math.isfinite(x): raise ValueError(...)
return x
```
