## Hint 1

If a colleague had only your definition and the table, what would they still have to guess? Go through the ingredients of
section 7.1: numerator, denominator, date basis, time zone, exclusions, owner, version. Which job statuses exist in QuickFix,
and what should happen to each of them?

## Hint 2

```text
Name, version, owner (one line)
Numerator: ...                         Denominator: ... (is the numerator inside it?)
Date basis: <column> in <time zone>    Period: start <= t < end
Statuses: completed / cancelled / failed / pending -> in or out, and why
Immature jobs: a rule (age limit, or report pending beside the rate)
Last: how would the two managers' numbers differ? (denominator? date basis? time zone?)
```
