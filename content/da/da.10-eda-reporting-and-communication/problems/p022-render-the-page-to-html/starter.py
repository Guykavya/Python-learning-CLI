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

import base64
import html
from pathlib import Path


def render_html(f, source_note, figures_dir):
    """One self-contained HTML page: escaped text, six <h3> sections, figures embedded as base64."""
    raise NotImplementedError
