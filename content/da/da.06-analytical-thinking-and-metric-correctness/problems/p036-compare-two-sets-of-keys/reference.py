def compare_keys(a, b, name_a="A", name_b="B"):
    sa = {k.item() if hasattr(k, "item") else k for k in a}
    sb = {k.item() if hasattr(k, "item") else k for k in b}
    only_a, only_b, both = sa - sb, sb - sa, sa & sb
    counts = {"a": len(sa), "b": len(sb), "only_a": len(only_a), "only_b": len(only_b), "both": len(both)}
    summary = (f"{name_a}: {len(sa)} | {name_b}: {len(sb)} | in both: {len(both)} | "
               f"only {name_a}: {len(only_a)} | only {name_b}: {len(only_b)}")
    return {"only_a": sorted(only_a), "only_b": sorted(only_b), "both": sorted(both), "counts": counts, "summary": summary}
