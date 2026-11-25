def bridge(start_label, start_value, steps, end_label, end_value):
    lines = ["step | change | running | check", " | ".join([start_label, "", str(start_value), ""]).rstrip()]
    running = start_value
    for label, change in steps:
        running += change
        lines.append(" | ".join([label, f"{change:+d}", str(running), ""]).rstrip())
    gap = running - end_value
    if gap != 0:
        raise ValueError(f"UNEXPLAINED {gap:+d}: bridge from {start_label} does not reach {end_label}")
    lines.append(" | ".join([f"= {end_label}", "", str(end_value), "OK"]))
    return "\n".join(lines)
