## Approach

The four log lines map one-to-one onto the four clauses. `else` holds the success work, so a
failed step can never log "done". `finally` runs on every exit: after success, after a handled
`ValueError`, and while any other exception is on its way out, which is exactly the guarantee
the problem asks for.

## Code

```python
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
```

## Complexity

O(number of steps), plus the steps' own work.

## Another way

Without `finally` you would need `log.append(f"end {name}")` in three places, and also an
`except Exception: log...; raise` clause to log it before other exceptions escape. `finally`
says it once and cannot be forgotten on a new path.
