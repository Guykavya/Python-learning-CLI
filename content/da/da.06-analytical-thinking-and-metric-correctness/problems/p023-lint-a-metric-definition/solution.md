## Approach

A linter is a list of small independent checks that each append a message. Keep the order fixed (missing, vague, closed
interval, time zone) so the output is stable and easy to compare in a test.

- A helper `_text(spec, field)` turns "absent", `None` and blank into the empty string, so one test `== ""` covers all three.
- "Has a rule" means a digit or one of `= < >`: a number or a comparison turns a word like *active* into a testable condition.
- The closed-interval test uses a regular expression, `<=` then optional spaces and quote, then a digit. A plain
  search for `<=` would wrongly flag the correct text `start <= t < end`.

## Code

```python
import re

REQUIRED = ["name", "question", "grain", "numerator", "denominator", "date_basis", "period", "exclusions", "owner", "version"]
VAGUE = ["active", "recent", "valid"]


def _text(spec, field):
    value = spec.get(field)
    return "" if value is None else str(value).strip()


def lint_definition(spec):
    problems = []
    for field in REQUIRED:
        if not _text(spec, field):
            problems.append(f"missing: {field}")
    for field in ["numerator", "denominator", "exclusions"]:
        text = _text(spec, field)
        has_rule = any(ch.isdigit() or ch in "=<>" for ch in text)
        for word in VAGUE:
            if word in text.lower() and not has_rule:
                problems.append(f"vague: {field} uses '{word}' without a rule")
    period = _text(spec, "period")
    if period and ("between" in period.lower() or re.search(r"<=\s*['\"]?\d", period)):
        problems.append("closed interval: write the period as start <= t < end")
    if not _text(spec, "time_zone") and "UTC" not in _text(spec, "date_basis") and "IST" not in _text(spec, "date_basis"):
        problems.append("no time zone: say UTC or IST")
    return problems
```

## Complexity

O(number of fields x number of vague words x text length): a handful of string searches. Nothing grows with the data.

## Another way

Make each check a small function that returns a list, and have `lint_definition` concatenate them
(`return check_missing(s) + check_vague(s) + ...`). A new rule is then one new function and one new test. Real
data-quality tools (and the `pandera` schemas of da.05) work the same way: many small named checks, one report.
