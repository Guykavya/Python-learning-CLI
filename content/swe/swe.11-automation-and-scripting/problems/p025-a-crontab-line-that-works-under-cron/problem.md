# A crontab line that works under cron

Chapter sections 12.1 (cron) and 12.2 (why a script works by hand and fails in cron). Cron runs your command with a tiny `PATH`, in your home folder, with no terminal. Most "it works by hand but not in cron" bugs disappear if every crontab line follows one pattern:

```text
<schedule> cd <project folder> && <absolute python> <absolute script> <args> >> <absolute log> 2>&1
```

Write a function that builds such lines, and refuses the ones that would break.

## What to write

```python
def cron_line(schedule, python, script, log, args=()) -> str: ...
```

- `schedule` is either five fields (`"30 2 * * 1-5"`, extra spaces between fields are collapsed to one) or a single shortcut word starting with `@` (`"@daily"`, `"@reboot"`). Anything else raises `ValueError`.
- `python`, `script` and `log` must be **absolute** paths, otherwise `ValueError` with the word `absolute` in the message. Cron runs on Linux and macOS, so judge them as POSIX paths with `PurePosixPath(p).is_absolute()` (this also works when the tests run on Windows).
- No path and no argument may contain a space: a crontab line is shell code, and an unquoted space splits it. Raise `ValueError`.
- The **project folder** is the script's parent folder; the command first `cd`s into it, so relative paths inside the script work.
- Both streams are **appended** to the log: `>> log 2>&1`.
- Every `%` in the command part is written as `\%`, because cron turns an unescaped `%` into a newline. (The schedule never contains `%`.)

## Example

```python
cron_line("30 2 * * 1-5", "/home/me/venv/bin/python", "/home/me/auto/tidy.py", "/home/me/auto/tidy.log",
          args=["organize", "/home/me/Downloads"])
# '30 2 * * 1-5 cd /home/me/auto && /home/me/venv/bin/python /home/me/auto/tidy.py organize /home/me/Downloads >> /home/me/auto/tidy.log 2>&1'

print(cron_line("@daily", "/usr/bin/python3", "/opt/r/report.py", "/var/log/r.log", args=["--stamp=%F"]))
# @daily cd /opt/r && /usr/bin/python3 /opt/r/report.py --stamp=\%F >> /var/log/r.log 2>&1

cron_line("@daily", "python3", "/opt/r/report.py", "/var/log/r.log")     # ValueError: python must be an absolute path
```
