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
