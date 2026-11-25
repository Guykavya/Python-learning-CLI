# Actionable or not?

Chapter section 6.4. A small **linter** checks the mechanical rules of a finding: a number and a comparison in the headline, an owner and a date for the action,
at least two limitations. This program is a shortened version of the chapter's `lint_finding`.

```python
import re
from dataclasses import dataclass


@dataclass
class Finding:
    headline: str
    owner: str
    by: str
    limitations: list


def lint(f):
    issues = []
    if not re.search(r"\d", f.headline):
        issues.append("no number")
    if not re.search(r"\b(from|to|than|vs)\b", f.headline):
        issues.append("no comparison")
    if not f.owner:
        issues.append("no owner")
    if not re.search(r"\d{4}-\d{2}-\d{2}", f.by):
        issues.append("no date")
    if len(f.limitations) < 2:
        issues.append("fewer than two limitations")
    return issues


findings = [
    Finding("Churn rose from 4.0% to 5.7%", "Head of Operations", "2025-01-31", ["observational", "one year"]),
    Finding("Churn is up", "", "soon", []),
    Finding("Churn rose by 1.7 points", "Ops", "31 January 2025", ["observational"]),
    Finding("Deliveries were late more often than before", "Ops", "2025-01-31", ["a", "b", "c"]),
]
for i, f in enumerate(findings, 1):
    print(i, lint(f))
```

Hand-trace the program, then write **every line it prints**, in order, in `answer.txt`. Do not run the code before you have written your answer.

## Example

A finding `Finding("Churn hit 6%", "Ops", "2025-02-01", ["x", "y"])` would print `5 ['no comparison']` if it were the fifth.

## After you answer

- Which of the four findings could a manager act on?
- The third finding has a perfectly readable date. Why does the linter complain, and is that a problem with the finding or with the linter?
