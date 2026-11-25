# The decision

Chapter section 2.11. A test ends with an interval for the **primary metric** and intervals for the **guardrail metrics** (things you refuse to hurt, like the on-time rate or the return rate). The decision follows rules fixed in advance.

Write `decide(primary_ci, guardrail_cis, mei)`:

- `primary_ci = (lo, hi)`: the interval of the lift of the primary metric; `mei`: the **minimum effect** that makes the change worth it;
- `guardrail_cis`: a dict `{name: (lo, hi, limit)}`: the interval of the change in a guardrail metric and the **limit** (usually negative) below which the change would be unacceptable.

Return `(decision, reason)`. Apply the rules **in this order**:

1. some guardrail has `hi < limit` (the whole interval is below its limit): `("do not ship", "guardrail <name> is below its limit")`;
2. `primary hi < mei`: `("do not ship", "the whole interval is below the minimum effect")`;
3. `primary lo > mei` and every guardrail has `lo >= limit`: `("ship", "the whole interval is above the minimum effect and the guardrails hold")`;
4. `primary lo > mei` but a guardrail has `lo < limit <= hi` (name the first such one, in dict order): `("extend the test", "guardrail <name> is not yet clear")`;
5. anything else: `("extend the test", "the interval contains the minimum effect")`.

## Example

`decide((0.8, 1.9), {"returns": (-0.4, 0.3, -1.0)}, 0.5)` is `("ship", "the whole interval is above the minimum effect and the guardrails hold")`.
