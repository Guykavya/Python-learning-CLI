def decide(primary_ci, guardrail_cis, mei):
    p_lo, p_hi = primary_ci
    for name, (lo, hi, limit) in guardrail_cis.items():
        if hi < limit:
            return "do not ship", f"guardrail {name} is below its limit"
    if p_hi < mei:
        return "do not ship", "the whole interval is below the minimum effect"
    unclear = [name for name, (lo, hi, limit) in guardrail_cis.items() if lo < limit]
    if p_lo > mei and not unclear:
        return "ship", "the whole interval is above the minimum effect and the guardrails hold"
    if p_lo > mei:
        return "extend the test", f"guardrail {unclear[0]} is not yet clear"
    return "extend the test", "the interval contains the minimum effect"
