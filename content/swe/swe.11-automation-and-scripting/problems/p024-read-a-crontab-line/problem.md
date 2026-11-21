# Read a crontab line

Chapter sections 12.1 (cron: the five fields, `*/15`, ranges, `@reboot`), 12.2 (why a script works by hand and fails in cron: the `%` row) and "Try it: read a crontab line". Before you trust a job to cron, say exactly when it will run.

Reminder of the five fields: `minute hour day-of-month month day-of-week`, where day-of-week `0` is Sunday and `1-5` is Monday to Friday. The calendar: **Friday 2026-11-20**, Monday 2026-11-23, Tuesday 2026-12-01, Friday 2027-01-01, Monday 2027-02-01.

Your crontab:

```text
*/15 * * * *  /home/me/venv/bin/python /home/me/check_inbox.py
0 9 * * 1-5   /home/me/venv/bin/python /home/me/standup.py
30 2 1 * *    /home/me/venv/bin/python /home/me/invoices.py
@reboot       /home/me/venv/bin/python /home/me/sync.py
0 8 * * *     /home/me/venv/bin/python /home/me/backup.py --name backup-$(date +%F).tar >> /home/me/backup.log 2>&1
```

1 to 3. It is **Friday 2026-11-20, 23:50**. For each of the first three lines, give the **next three** times it runs.

4. When does the fourth line run? Choose one:
   - A. every day at midnight
   - B. once, at the first 00:00 after the machine was restarted
   - C. once each time the machine (the cron daemon) starts, and never on a clock schedule
   - D. every minute until the machine is restarted

5. The fifth line never produces the file the author expects. Why? Choose one:
   - A. `$(...)` is not allowed in a crontab
   - B. cron turns every unescaped `%` into a newline, so the command ends at `+` and the rest is fed to it as input; it must be written `\%`
   - C. `0 8 * * *` means 08:00 on Sundays only
   - D. `2>&1` must be written before `>>`

## Answer format

Five lines. Lines 1 to 3: the number, a colon and a space, then the three times as `Sat 2026-11-21 00:00` (short weekday, date, 24-hour time) separated by ` | `. Lines 4 and 5: the number, a colon, a space and the letter.

```text
1: Sat 2026-11-21 00:00 | ... | ...
2: ...
3: ...
4: ?
5: ?
```
