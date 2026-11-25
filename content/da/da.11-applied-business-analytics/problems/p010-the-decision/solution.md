## Approach

Guardrails come first: a harm outweighs any gain. Then the primary metric against the minimum effect, judged by the **whole interval**, not by the point estimate. An interval that contains the minimum effect means "we do not know yet".

## Code

```python
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
```

## Complexity

O(guardrails).

## Another way

Add the money: translate the interval into contribution per month and the guardrail into a cost (section 2.11 does this for the banner), then decide on the net value.
