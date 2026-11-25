def rates_by_group(rows):
    counts = {}
    totals = {}
    for group, treatment, success in rows:
        if treatment not in ("A", "B"):
            raise ValueError(f"unknown treatment: {treatment!r}")
        cell = counts.setdefault(group, {}).setdefault(treatment, [0, 0])
        cell[1] += 1
        cell[0] += 1 if success else 0
        total = totals.setdefault(treatment, [0, 0])
        total[1] += 1
        total[0] += 1 if success else 0
    groups = {}
    for group, by_treatment in counts.items():
        if set(by_treatment) != {"A", "B"}:
            raise ValueError(f"group {group!r} needs both treatments")
        groups[group] = {t: s / n for t, (s, n) in by_treatment.items()}
    if not groups:
        raise ValueError("no rows")
    overall = {t: s / n for t, (s, n) in totals.items()}
    group_winners = set()
    for rates in groups.values():
        if rates["A"] > rates["B"]:
            group_winners.add("A")
        elif rates["B"] > rates["A"]:
            group_winners.add("B")
        else:
            group_winners.add("tie")
    overall_winner = "A" if overall["A"] > overall["B"] else "B" if overall["B"] > overall["A"] else "tie"
    paradox = (len(group_winners) == 1 and "tie" not in group_winners
               and overall_winner != "tie" and overall_winner not in group_winners)
    return {"groups": groups, "overall": overall, "paradox": paradox}
