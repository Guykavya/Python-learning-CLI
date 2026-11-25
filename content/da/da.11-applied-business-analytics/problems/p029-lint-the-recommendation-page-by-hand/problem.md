# Lint the recommendation page by hand

Chapter section 6.4. The recommendation page of the ShopNest analysis is checked by a small linter before it goes out. Here is the linter and a **draft** with four planted faults. Read the linter's rules carefully: some use regular expressions.

```python
import re
from dataclasses import dataclass


@dataclass
class Finding:
    headline: str
    recommendations: list
    impact: str
    evidence: list
    confidence: str
    limitations: list
    next_steps: list

    def render_markdown(self):
        lines = ["# " + self.headline, "", "### Recommendation"]
        lines += [f"- **{r['action']}** (owner: {r['owner']}; by {r['by']})" for r in self.recommendations]
        lines += ["", "### Impact", self.impact, "", "### Evidence"] + [f"- {e}" for e in self.evidence]
        lines += ["", "### Confidence", self.confidence, "", "### Limitations"] + [f"- {l}" for l in self.limitations]
        lines += ["", "### Next steps"] + [f"- {n}" for n in self.next_steps]
        return "\n".join(lines)


def lint_finding(f, max_words=450):
    issues = []
    if not re.search(r"\d", f.headline):
        issues.append("headline has no number")
    for i, r in enumerate(f.recommendations):
        if not r.get("owner"):
            issues.append(f"recommendation {i + 1} has no owner")
        if not re.search(r"\d{1,2} \w+ \d{4}", str(r.get("by", ""))):
            issues.append(f"recommendation {i + 1} has no date")
    if not re.search(r"\d.*\b(to|between)\b.*\d", f.impact):
        issues.append("impact is a point, not a range")
    if len(f.evidence) < 2 or not all(re.search(r"\d", e) for e in f.evidence):
        issues.append("evidence needs at least two items, each with a number")
    if not any(re.search(r"CI|interval|range", e) for e in f.evidence):
        issues.append("no evidence item carries its uncertainty")
    if len(f.limitations) < 2:
        issues.append("fewer than two limitations")
    if not any(re.search(r"success|measure|within", n) for n in f.next_steps):
        issues.append("no success measure in the next steps")
    for phrase in ("monitor the situation", "further analysis", "look into", "it seems"):
        if phrase in f.render_markdown().lower():
            issues.append(f"vague phrase: {phrase!r}")
    if len(f.render_markdown().split()) > max_words:
        issues.append(f"too long for one page: {len(f.render_markdown().split())} words")
    return issues


draft = Finding(
    headline="Fix mobile checkout first: it could add 120 to 340 orders a month",
    recommendations=[
        {"action": "Redesign the mobile cart-to-checkout step", "owner": "Head of Product", "by": "28 February 2025"},
        {"action": "Hold the banner and test a threshold version", "owner": "Head of Growth", "by": "soon"},
    ],
    impact="The mobile fix is worth about 40,000 rupees of contribution a month.",
    evidence=["Mobile sessions start checkout 45% of the time against 66% on desktop (95% CI 44% to 46%).",
              "The banner test found conversion +0.58 points.",
              "RFM segments predict future spend."],
    confidence="High for the mobile gap.",
    limitations=["The data are synthetic.", "We should look into returns data next."],
    next_steps=["Powered A/B test of the new checkout.", "Success measure: mobile cart-to-checkout rate above 55% within three months."],
)
for issue in lint_finding(draft):
    print(issue)
print(len(lint_finding(draft)))
```

Hand-trace the program, then write **every line it prints**, in order, in `answer.txt`. Do not run the code before you have written your answer.

## Example

If the only fault were a missing owner on the first recommendation, the program would print `recommendation 1 has no owner` and then `1`.

## After you answer

- Which fault is a **content** problem that a person must fix, and which could be caught by a better regular expression?
- The linter does not complain that the second limitation is weak. What would a human reviewer add?
