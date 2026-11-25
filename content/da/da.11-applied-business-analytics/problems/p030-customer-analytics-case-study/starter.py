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


import numpy as np
import pandas as pd
from scipy import stats


def two_prop(kA, nA, kB, nB, level=0.95):
    pA, pB = kA / nA, kB / nB
    diff = pB - pA
    se = np.sqrt(pA * (1 - pA) / nA + pB * (1 - pB) / nB)
    z = stats.norm.ppf(1 - (1 - level) / 2)
    pp = (kA + kB) / (nA + nB)
    z_stat = diff / np.sqrt(pp * (1 - pp) * (1 / nA + 1 / nB))
    return {"A": float(pA), "B": float(pB), "diff": float(diff), "lo": float(diff - z * se), "hi": float(diff + z * se),
            "rel_lift": float(diff / pA), "p": float(2 * stats.norm.sf(abs(z_stat)))}


def repeat_rate_90d(orders, customers, asof):
    asof = pd.Timestamp(asof)
    elig = customers[customers["first_order"] <= asof - pd.Timedelta(days=90)]
    o = orders.sort_values(["customer_id", "order_date"])
    second = o.groupby("customer_id")["order_date"].nth(1)
    second.index = o.loc[second.index, "customer_id"].to_numpy()
    d = elig.set_index("customer_id")["first_order"]
    gap = (second.reindex(d.index) - d).dt.days
    repeaters = int((gap <= 90).sum())
    n = len(elig)
    return {"eligible": int(n), "repeaters": repeaters, "rate_pct": repeaters / n * 100 if n else float("nan")}


def rfm_table(orders, customers, asof):
    asof = pd.Timestamp(asof)
    od = orders[orders["order_date"] <= asof]
    g = od.groupby("customer_id").agg(last=("order_date", "max"), F=("amount", "size"), M=("amount", "sum"))
    g["R"] = (asof - g["last"]).dt.days.astype(int)
    g = g[g.index.isin(customers["customer_id"])]
    return g[["R", "F", "M"]].sort_index()


def score_quantile(s, higher_is_better=True, n=5):
    r = s.rank(method="first", ascending=higher_is_better)
    return pd.qcut(r, n, labels=list(range(1, n + 1))).astype(int)


def segment(r, f):
    if r >= 4 and f >= 4:
        return "Champions"
    if r >= 3 and f >= 3:
        return "Loyal"
    if r >= 4 and f <= 2:
        return "New / promising"
    if r <= 2 and f >= 3:
        return "At risk"
    if r <= 2 and f <= 2:
        return "Hibernating"
    return "Needs attention"


SEGMENTS = ["Champions", "Loyal", "New / promising", "Needs attention", "At risk", "Hibernating"]
DEC = r"[+-]?\d[\d,]*\.\d+"          # decimal numbers such as 5.3, +0.58, -0.03 or 1,250.5


def build_case_study(data):
    """(finding, page, results) from data = {'exp', 'sessions', 'customers', 'orders', 'asof'}; see the statement."""
    raise NotImplementedError


def check_case_study(page, results):
    """Problems of a page: expected strings that are missing, then decimal numbers that are not in results['decimals']."""
    raise NotImplementedError
