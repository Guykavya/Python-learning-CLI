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


def build_report(R):
    return Finding(
        headline=f"Monthly churn rose from {R['churn_before']:.1f}% to {R['churn_after']:.1f}% in Sep-Dec 2024, mainly because of late deliveries",
        recommendations=[{"action": "Restore on-time delivery (courier contract review)", "owner": "Head of Operations", "by": "31 January 2025"}],
        impact=f"Fixing it keeps about {R['saved']:.0f} customers (range {R['saved_lo']:.0f} to {R['saved_hi']:.0f}) a month.",
        evidence=[f"Customers with a recent late box leave {R['rr']:.1f} times as often (95% CI {R['rr_lo']:.1f} to {R['rr_hi']:.1f}).",
                  f"On-time delivery fell from {R['ontime_before']:.0f}% to {R['ontime_after']:.0f}% in the same month."],
        confidence="High for the main cause; the price effect is uncertain.",
        limitations=list(R["limitations"]),
        next_steps=[f"Success measure: monthly churn back to {R['churn_before']:.1f}% within three months."],
    )
