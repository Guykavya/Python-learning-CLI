## Approach

Every number comes from one computation and is formatted **once**; the same strings go into the page and into `results`, so they cannot disagree. The check is a safety net for edits made after the build: it looks for the strings that must be there and for decimal numbers nobody computed.

## Code

```python


def build_case_study(data):
    exp, ses, cus, orders, asof = data["exp"], data["sessions"], data["customers"], data["orders"], data["asof"]
    g = exp.groupby("variant")["converted"].agg(["sum", "size"])
    ab = two_prop(int(g.loc["A", "sum"]), int(g.loc["A", "size"]), int(g.loc["B", "sum"]), int(g.loc["B", "size"]))
    diff, lo, hi = ab["diff"] * 100, ab["lo"] * 100, ab["hi"] * 100
    mob = ses[ses["device"] == "mobile"]
    des = ses[ses["device"] == "desktop"]
    mobile = mob[mob["added_to_cart"]]["started_checkout"].mean() * 100
    desktop = des[des["added_to_cart"]]["started_checkout"].mean() * 100
    repeat = {}
    for ch in sorted(cus["channel"].unique()):
        sub = cus[cus["channel"] == ch]
        repeat[ch] = repeat_rate_90d(orders[orders["customer_id"].isin(sub["customer_id"])], sub, asof)["rate_pct"]
    t = rfm_table(orders, cus, asof)
    t["R_score"] = score_quantile(t["R"], higher_is_better=False)
    t["F_score"] = pd.cut(t["F"], [0, 1, 2, 3, 5, np.inf], labels=[1, 2, 3, 4, 5]).astype(int)
    seg = pd.Series([segment(r, f) for r, f in zip(t["R_score"], t["F_score"])]).value_counts()
    counts = {s: int(seg.get(s, 0)) for s in SEGMENTS}

    ab_text = f"{diff:+.2f} points (95% CI {lo:+.2f} to {hi:+.2f})"
    fun_text = f"{mobile:.0f}% against {desktop:.0f}%"
    best = max(repeat, key=repeat.get)
    finding = Finding(
        headline=f"Mobile starts checkout for {mobile:.0f}% of carts against {desktop:.0f}% on desktop, and the banner moved conversion by {diff:+.2f} points",
        recommendations=[{"action": "Redesign the mobile cart-to-checkout step and test it", "owner": "Head of Product", "by": "31 March 2025"},
                         {"action": "Hold the free-shipping banner until a powered test is done", "owner": "Head of Growth", "by": "30 April 2025"}],
        impact=f"The banner interval runs from {lo:+.2f} to {hi:+.2f} points of conversion; the mobile gap is {desktop - mobile:.0f} points of carts.",
        evidence=[f"Mobile carts reach checkout {fun_text}.",
                  f"Banner test: conversion difference {ab_text}, p = {ab['p']:.2f}.",
                  f"90-day repeat rate is highest for {best} customers ({repeat[best]:.1f}%)."],
        confidence="High for the mobile gap; low for the banner, whose interval includes zero.",
        limitations=["The data are a small synthetic sample.", "Margin and acquisition costs are assumptions from other teams."],
        next_steps=["Powered A/B test of the new mobile checkout.", "Success measure: mobile cart-to-checkout rate within 5 points of desktop in three months."])
    parts = [finding.render_markdown(), "", "## Retention by channel (90-day repeat rate)"]
    parts += [f"- {ch}: {rate:.1f}%" for ch, rate in repeat.items()]
    parts += ["", "## RFM segments (customers)"] + [f"- {s}: {n:,}" for s, n in counts.items()]
    page = "\n".join(parts)
    results = {"ab": ab_text, "funnel": fun_text, "repeat": repeat, "segments": counts,
               "expected": [ab_text, fun_text] + [f"{ch}: {r:.1f}%" for ch, r in repeat.items()] + [f"{s}: {n:,}" for s, n in counts.items()],
               "decimals": sorted(set(re.findall(DEC, page)))}
    return finding, page, results


def check_case_study(page, results):
    problems = [f"missing: {text}" for text in results["expected"] if text not in page]
    seen = []
    for tok in re.findall(DEC, page):
        if tok not in results["decimals"] and tok not in seen:
            seen.append(tok)
            problems.append(f"number not in the results: {tok}")
    return problems
```

(The given helpers `Finding`, `lint_finding`, `two_prop`, `repeat_rate_90d`, `rfm_table`, `score_quantile`, `segment`, `SEGMENTS`, `DEC` stay above it.)

## Complexity

Dominated by the group-bys: O(n log n).

## Another way

Put each analysis in its own function that returns a small dict and have `build_case_study` assemble them; that makes each part testable on its own (problems 5, 14, 19 and 23 are exactly those parts).
