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
    e = html.escape
    p = ["<!doctype html>", "<html lang='en'><head><meta charset='utf-8'><title>Finding</title></head><body>",
         f"<h1>{e(f.headline)}</h1>", "<h3>Recommendation</h3>", "<ul>"]
    p += [f"<li>{e(r['action'])} (owner: {e(r['owner'])}; by {e(r['by'])})</li>" for r in f.recommendations]
    p += ["</ul>", "<h3>Impact</h3>", f"<p>{e(f.impact)}</p>"]
    for name in f.figures:
        b64 = base64.b64encode((Path(figures_dir) / name).read_bytes()).decode("ascii")
        p.append(f"<img src='data:image/png;base64,{b64}' alt='{e(name, quote=True)}'>")
    p += ["<h3>Evidence</h3>", "<ul>"] + [f"<li>{e(x)}</li>" for x in f.evidence] + ["</ul>"]
    p += ["<h3>Confidence</h3>", f"<p>{e(f.confidence)}</p>"]
    p += ["<h3>Limitations</h3>", "<ul>"] + [f"<li>{e(x)}</li>" for x in f.limitations] + ["</ul>"]
    p += ["<h3>Next steps</h3>", "<ul>"] + [f"<li>{e(x)}</li>" for x in f.next_steps] + ["</ul>"]
    p += [f"<p><small>{e(source_note)}</small></p>", "</body></html>"]
    return "\n".join(p)
