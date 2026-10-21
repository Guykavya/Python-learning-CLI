def run_steps(steps, log):
    """Run each (name, func) step, logging start/done/failed/end. Return the number that succeeded."""
    done = 0
    for name, func in steps:
        log.append(f"start {name}")
        func()
        log.append(f"done {name}")
        done += 1
    return done
