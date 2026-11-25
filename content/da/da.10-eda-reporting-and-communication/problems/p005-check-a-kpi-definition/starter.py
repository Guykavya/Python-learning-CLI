REQUIRED = ["name", "numerator", "grain", "owner", "direction", "type", "unit"]
TYPES = {"leading", "lagging", "guardrail", "vanity"}


def check_kpi(defn):
    """List of problems with a KPI definition dict (see the statement); [] when it is complete."""
    raise NotImplementedError
