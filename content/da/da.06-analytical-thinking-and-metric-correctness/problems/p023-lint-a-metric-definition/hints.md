## Hint 1

Which four checks are there, and in which order must their messages appear? For the "missing" check, what must you do
with `None`, with `"   "`, and with a key that is not in the dict at all, so that one rule covers all three? How can you
say "this text contains a rule" in one line, using the characters in the statement?

## Hint 2

```text
problems = []
for field in REQUIRED:                       # fixed order
    text = (spec.get(field) or "").strip()
    if text == "": problems.append("missing: " + field)
for field in numerator, denominator, exclusions:
    text = ... ; has_rule = any(c.isdigit() or c in "=<>" for c in text)
    for word in active, recent, valid:
        if word in text.lower() and not has_rule: append the vague message
period: "between" in lower text, or re.search(r"<=\s*['\"]?\d", text)
time zone: time_zone empty AND "UTC" not in date_basis AND "IST" not in date_basis
```
