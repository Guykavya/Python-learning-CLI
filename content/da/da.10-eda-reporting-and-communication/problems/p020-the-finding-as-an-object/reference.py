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
    return Finding(
        headline=(f"Monthly churn rose from {R['churn_before']:.1f}% to {R['churn_after']:.1f}% in Sep-Dec 2024, almost entirely because "
                  f"on-time delivery fell from {R['ontime_before']:.0f}% to {R['ontime_after']:.0f}%"),
        recommendations=[{"action": f"Restore the on-time rate to {R['ontime_before']:.0f}% (review the courier contract first)",
                          "owner": "Head of Operations", "by": "31 January 2025"}],
        impact=(f"Each month of delay costs about {R['saved']:.0f} customers (range {R['saved_lo']:.0f} to {R['saved_hi']:.0f}). "
                "The cost of the fix is not yet known."),
        evidence=[f"Customers with a late box in the last 3 weeks leave {R['rr']:.1f} times as often (95% CI {R['rr_lo']:.1f} to {R['rr_hi']:.1f}).",
                  f"Late boxes account for {R['late_pts']:.1f} points (95% CI {R['late_pts_lo']:.1f} to {R['late_pts_hi']:.1f}) of the rise in monthly churn."],
        confidence="High for late deliveries as the main cause: timing, size and a stable rate ratio agree.",
        limitations=["Observational data: customers were not randomly assigned late boxes.",
                     "We do not know whether one late box or its handling drives the exit."],
        next_steps=["Operations to split late boxes by courier and city this month.",
                    f"Success measure: monthly churn back to {R['churn_before']:.1f}% within three months of the fix."],
    )
