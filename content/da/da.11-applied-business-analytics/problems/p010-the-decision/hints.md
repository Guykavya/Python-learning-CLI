## Hint 1

Write the rules as `if` statements in the order of the list: the first one that applies decides. For rule 4, which two conditions together say "the guardrail interval straddles its limit"?

## Hint 2

```text
for name, (lo, hi, limit) in guardrails: if hi < limit: return ("do not ship", ...)
if p_hi < mei: ...
bad = [name for ... if lo < limit]       # lo < limit <= hi here, since rule 1 removed hi < limit
if p_lo > mei and not bad: ship; if p_lo > mei: extend (guardrail unclear); else extend
```
