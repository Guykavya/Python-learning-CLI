## Approach

```python
def cron_line(schedule, python, script, log, args=()):
    fields = schedule.split()
    if not (len(fields) == 5 or (len(fields) == 1 and fields[0].startswith("@"))):
        raise ValueError(f"a schedule has 5 fields or is one @word: {schedule!r}")
    for name, value in (("python", python), ("script", script), ("log", log)):
        if not PurePosixPath(str(value)).is_absolute():
            raise ValueError(f"{name} must be an absolute path: {value}")
    words = [str(python), str(script)] + [str(a) for a in args]
    for word in words + [str(log)]:
        if " " in word:
            raise ValueError(f"no spaces allowed in a crontab command: {word!r}")
    project = PurePosixPath(str(script)).parent
    command = f"cd {project} && {' '.join(words)} >> {log} 2>&1"
    return " ".join(fields) + " " + command.replace("%", "\\%")
```

Each part answers one row of the table in section 12.2: **absolute interpreter** (cron's `PATH` is `/usr/bin:/bin`, and you want the virtualenv's Python with your packages), **absolute script and `cd`** (cron starts in your home folder), **`>> log 2>&1`** (otherwise output vanishes or is mailed to a mailbox nobody reads), **`\%`** (cron's newline rule). Refusing bad input at build time is cheaper than discovering at 3 a.m. that the job never ran.

## Complexity

O(length of the line).

## Another way

Keep the crontab line minimal and put the logic in a wrapper script: `0 8 * * * /home/me/auto/run.sh`, where `run.sh` sets `PATH`, `cd`s, activates the environment and redirects output. Then there is no `%` or quoting in the crontab at all, and you can run `run.sh` by hand to test exactly what cron will run. Allowing spaces properly means quoting each word with `shlex.quote`.
