"""The chapter's finding linter (section 6.4), used by the tests as the specification."""
import re

VAGUE = ["monitor the situation", "further analysis", "look into", "it seems", "some observations", "as can be seen", "interesting"]


def lint_finding(f, max_words=400):
    issues = []
    h = f.headline
    if not re.search(r"\d", h):
        issues.append("headline has no number")
    if not re.search(r"\b(from|to|than|against|vs)\b|%", h):
        issues.append("headline gives no comparison (from X to Y)")
    if len(h.split()) > 40:
        issues.append(f"headline is {len(h.split())} words (more than 40)")
    if not f.recommendations:
        issues.append("no recommendation")
    for i, r in enumerate(f.recommendations):
        if not r.get("owner"):
            issues.append(f"recommendation {i + 1} has no owner")
        if not re.search(r"\d{1,2} \w+ \d{4}|\d{4}-\d{2}-\d{2}", str(r.get("by", ""))):
            issues.append(f"recommendation {i + 1} has no date")
    if not re.search(r"\d.*\b(to|between|-)\b.*\d|\brange\b", f.impact):
        issues.append("impact is a point, not a range")
    if not re.search(r"\b(customers|rupees|%|points)\b", f.impact):
        issues.append("impact is not in business units")
    if len(f.evidence) < 2 or not all(re.search(r"\d", e) for e in f.evidence):
        issues.append("evidence needs at least two items, each with a number")
    if not any(re.search(r"CI|interval|range", e) for e in f.evidence):
        issues.append("no evidence item carries its uncertainty")
    if not f.confidence.strip():
        issues.append("no statement of confidence")
    if len(f.limitations) < 2:
        issues.append("fewer than two limitations")
    if not any(re.search(r"success|measure|%", n) for n in f.next_steps):
        issues.append("no success measure in the next steps")
    text = f.render_markdown().lower()
    for phrase in VAGUE:
        if phrase in text:
            issues.append(f"vague phrase: {phrase!r}")
    if len(text.split()) > max_words:
        issues.append(f"{len(text.split())} words: too long for one page (max {max_words})")
    return issues
