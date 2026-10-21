def run_steps(steps, log):
    """Run each (name, func) step, logging start/done/failed/end. Return the number that succeeded."""
    done = 0
    for name, func in steps:
        log.append(f"start {name}")
        try:
            func()
        except ValueError as e:
            log.append(f"failed {name}: {e}")
        else:
            log.append(f"done {name}")
            done += 1
        finally:
            log.append(f"end {name}")
    return done
