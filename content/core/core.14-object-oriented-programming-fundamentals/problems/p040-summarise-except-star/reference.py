def run_all(tasks):
    results = {}
    errors = []
    for name, func in tasks:
        try:
            results[name] = func()
        except Exception as err:
            err.add_note(f"task: {name}")
            errors.append(err)
    if errors:
        raise ExceptionGroup(f"{len(errors)} of {len(tasks)} tasks failed", errors)
    return results


def summarise(tasks):
    counts = {"ok": len(tasks), "value_errors": 0, "key_errors": 0, "other_errors": 0}
    try:
        run_all(tasks)
    except* ValueError as eg:
        counts["value_errors"] = len(eg.exceptions)
    except* KeyError as eg:
        counts["key_errors"] = len(eg.exceptions)
    except* Exception as eg:
        counts["other_errors"] = len(eg.exceptions)
    counts["ok"] -= counts["value_errors"] + counts["key_errors"] + counts["other_errors"]
    return counts
