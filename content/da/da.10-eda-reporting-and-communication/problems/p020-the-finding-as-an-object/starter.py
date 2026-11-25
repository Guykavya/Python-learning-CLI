from dataclasses import dataclass, field


@dataclass
class Finding:
    headline: str
    recommendations: list            # each: {"action": ..., "owner": ..., "by": ...}
    impact: str
    evidence: list                   # each: a sentence with a number
    confidence: str
    limitations: list
    next_steps: list
    figures: list = field(default_factory=list)

    def render_markdown(self):
        lines = ["# " + self.headline, "", "### Recommendation"]
        lines += [f"- **{r['action']}** (owner: {r['owner']}; by {r['by']})" for r in self.recommendations]
        lines += ["", "### Impact", self.impact, "", "### Evidence"] + [f"- {e}" for e in self.evidence]
        lines += ["", "### Confidence", self.confidence, "", "### Limitations"] + [f"- {l}" for l in self.limitations]
        lines += ["", "### Next steps"] + [f"- {n}" for n in self.next_steps]
        return "\n".join(lines)


def make_finding(R):
    """A Finding whose numbers all come from R and that passes lint_finding with no issues."""
    raise NotImplementedError
