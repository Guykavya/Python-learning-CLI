## Hint 1

Separate the pure question from the actions. `missed_days` only does date arithmetic: what do you add to a `date` to get the next day, and when does the loop stop? `run_daily` then reads the state, loops over that list, and writes the state after each success. Where does the `try` go so a failure stops the loop but keeps the days already done?

## Hint 2

```text
missed_days: today = now.date()
    if last_success is None: return [today]
    days = []; day = last_success + timedelta(days=1)
    while day <= today: days.append(day); day += timedelta(days=1)
    return days
run_daily:
    last = date.fromisoformat(state["last_success"]) if state file exists else None
    done = []
    for day in missed_days(last, now):
        try: job(day)
        except Exception: return done, day
        done.append(day); write_json_atomic(state_path, {"last_success": day.isoformat()})
    return done, None
```
