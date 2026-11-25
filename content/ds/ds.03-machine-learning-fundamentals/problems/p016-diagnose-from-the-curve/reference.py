def diagnose(lc, task="regression", floor=None):
    if task not in ("regression", "classification"):
        raise ValueError(f"unknown task {task!r}")
    last = lc.iloc[-1]
    error = (1 - last["validation"]) if task == "classification" else last["validation"]
    rel_gap = last["gap"] / max(abs(error), 1e-12)
    if rel_gap > 0.15:
        return "high variance"
    if floor is not None and error > 1.25 * floor:
        return "high bias"
    return "fine"
