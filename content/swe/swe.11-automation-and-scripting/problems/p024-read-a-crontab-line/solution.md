## Approach

Checked with the chapter's `Cron(expr).next_runs(datetime(2026, 11, 20, 23, 50), 3)` (section 12.1):

| Line | Pattern | In words | Next three |
|---|---|---|---|
| 1 | `*/15 * * * *` | every 15 minutes, all day, every day | Sat 00:00, 00:15, 00:30 |
| 2 | `0 9 * * 1-5` | 09:00, Monday to Friday | Mon 23, Tue 24, Wed 25 Nov at 09:00 |
| 3 | `30 2 1 * *` | 02:30 on the first day of every month | 1 Dec, 1 Jan, 1 Feb at 02:30 |
| 4 | `@reboot` | when the cron daemon starts (normally at boot), never on a clock | **C** |
| 5 | contains `%` | `%` is a newline to cron; the command breaks | **B** |

Line 5 in detail: cron cuts the command at the first unescaped `%`, so the shell runs `.../backup.py --name backup-$(date +` (a syntax error), and `F).tar >> ...` is sent to it as standard input. The fix is `\%F`, or better, compute the date **inside** the Python script (`date.today().isoformat()`), which also keeps the crontab line short. A problem with line 3 worth noticing too: 02:30 sits in the window where daylight saving time changes, so in some time zones it runs twice or not at all once a year (section 12.2).

## Cost

Reading only. Before installing a line, check it with `Cron(...).next_runs(...)` or a site such as crontab.guru, and run the exact command once in a clean environment (`env -i /bin/sh -c '...'`).

## Another way

Systemd timers (section 12.3) write the same schedules in words: `OnCalendar=Mon..Fri 09:00` and `OnCalendar=*-*-01 02:30`, and `systemd-analyze calendar "Mon..Fri 09:00"` prints the next run for you.
