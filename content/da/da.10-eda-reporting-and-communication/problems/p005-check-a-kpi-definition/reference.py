REQUIRED = ["name", "numerator", "grain", "owner", "direction", "type", "unit"]
TYPES = {"leading", "lagging", "guardrail", "vanity"}


def check_kpi(defn):
    issues = [f"missing field: {f}" for f in REQUIRED if not defn.get(f)]
    t = defn.get("type")
    if t and t not in TYPES:
        issues.append(f"unknown type: {t}")
    if t == "vanity":
        issues.append("vanity metric: no decision depends on it")
    d = defn.get("direction")
    if d and d not in ("up", "down"):
        issues.append("direction must be 'up' or 'down'")
    if defn.get("unit") == "%" and not defn.get("denominator"):
        issues.append("a percentage needs a denominator")
    return issues
